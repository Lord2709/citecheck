"""Background draft checks.  A draft with 10-20 citations takes from seconds to a minute (paper lookups, full text),
so the browser starts a job, then polls it and shows each citation as soon as it is done."""
from __future__ import annotations

import copy
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Optional

from src.report import summarize

JOB_TTL_SECONDS = 3600


@dataclass
class Job:
    id: str
    user_id: str
    run_id: str
    status: str = "queued"          # queued | running | done | error
    done: int = 0
    total: int = 0
    citations: list = field(default_factory=list)
    report: Optional[dict] = None
    error: str = ""
    created: float = field(default_factory=time.time)

    def view(self) -> dict:
        return {"id": self.id, "run_id": self.run_id, "status": self.status, "done": self.done, "total": self.total,
                "citations": list(self.citations), "report": self.report, "error": self.error,
                "summary": summarize(self.report) if self.report else summarize({"citations": list(self.citations)})}


class JobManager:
    def __init__(self, workers: int = 2, inline: bool = False):
        self.inline = inline                       # tests: run jobs in the calling thread
        self.pool = None if inline else ThreadPoolExecutor(max_workers=workers, thread_name_prefix="citecheck-job")
        self.jobs, self.lock = {}, threading.Lock()

    def get(self, job_id: str, user_id: str) -> Optional[Job]:
        with self.lock:
            j = self.jobs.get(job_id)
        return j if j and j.user_id == user_id else None

    def _cleanup(self):
        cutoff = time.time() - JOB_TTL_SECONDS
        with self.lock:
            for k in [k for k, j in self.jobs.items() if j.created < cutoff and j.status in ("done", "error")]:
                del self.jobs[k]

    def start_draft_check(self, agent, text: str, user_id: str, run_id: str, options: dict,
                          on_finish: Callable) -> Job:
        self._cleanup()
        job = Job(id=uuid.uuid4().hex, user_id=user_id, run_id=run_id)
        with self.lock:
            self.jobs[job.id] = job
        a = copy.copy(agent)                       # per-job switches; the models underneath are shared
        a.escalate = bool(options.get("read_full_text", True))
        a.suggest = bool(options.get("suggest", True))

        def progress(n, total):
            job.total = total

        def result(r):
            job.citations.append(r.to_dict())
            job.done = len(job.citations)

        def run():
            job.status = "running"
            t0 = time.time()
            try:
                rep = a.check_draft(text, max_citations=int(options.get("max_citations", 20)),
                                    progress=progress, on_result=result).to_dict()
                job.report, job.total, job.status = rep, len(rep["citations"]), "done"
                on_finish(job, rep, time.time() - t0, None)
            except Exception as e:  # reported to the browser, never a crash
                job.error, job.status = f"{type(e).__name__}: {str(e)[:200]}", "error"
                on_finish(job, None, time.time() - t0, job.error)

        if self.inline:
            run()
        else:
            self.pool.submit(run)
        return job
