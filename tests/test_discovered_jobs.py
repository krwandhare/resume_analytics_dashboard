from types import SimpleNamespace

from myproject import data_loader


class FakeQuery:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.calls = []

    def select(self, value):
        self.calls.append(("select", value))
        return self

    def is_(self, column, value):
        self.calls.append(("is", column, value))
        return self

    def order(self, column, desc=False):
        self.calls.append(("order", column, desc))
        return self

    def limit(self, value):
        self.calls.append(("limit", value))
        return self

    def insert(self, payload):
        self.calls.append(("insert", payload))
        return self

    def update(self, payload):
        self.calls.append(("update", payload))
        return self

    def eq(self, column, value):
        self.calls.append(("eq", column, value))
        return self

    def execute(self):
        self.calls.append(("execute",))
        return SimpleNamespace(data=self.rows)


class FakeClient:
    def __init__(self, rows=None):
        self.queries = {}
        self.rows = rows or []

    def table(self, name):
        query = self.queries.setdefault(name, FakeQuery(self.rows if name == "job_review_queue" else []))
        return query


def test_load_discovered_jobs_filters_orders_and_limits_at_source(monkeypatch):
    client = FakeClient([
        {
            "id": 7,
            "title": "Platform Engineer",
            "company": "Example",
            "source_url": "https://example.com/job",
            "discovered_at": "2026-08-11T12:00:00Z",
            "resolved_at": None,
        }
    ])
    monkeypatch.setattr(data_loader, "is_valid_supabase_config", lambda: (True, "ok"))
    monkeypatch.setattr(data_loader, "get_supabase_client", lambda: client)
    data_loader.load_discovered_jobs.clear()

    result = data_loader.load_discovered_jobs()

    assert result.loc[0, "job_title"] == "Platform Engineer"
    assert result.loc[0, "job_url"] == "https://example.com/job"
    assert ("is", "resolved_at", "null") in client.queries["job_review_queue"].calls
    assert ("order", "discovered_at", True) in client.queries["job_review_queue"].calls
    assert ("limit", 200) in client.queries["job_review_queue"].calls
    data_loader.load_discovered_jobs.clear()


def test_add_discovered_job_inserts_tracker_row_and_resolves_queue(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(data_loader, "get_supabase_client", lambda: client)

    ok, message = data_loader.add_discovered_to_tracker(
        7, " Platform Engineer ", " Example ", 85, " Notes ", " https://example.com/job "
    )

    assert ok is True
    assert "added to Job Tracker" in message
    job_insert = next(call[1] for call in client.queries["jobs"].calls if call[0] == "insert")
    assert job_insert["job_title"] == "Platform Engineer"
    assert job_insert["company"] == "Example"
    assert job_insert["status"] == "Applied"
    queue_calls = client.queries["job_review_queue"].calls
    assert any(call[0] == "update" and "resolved_at" in call[1] for call in queue_calls)
    assert ("eq", "id", 7) in queue_calls


def test_dismiss_discovered_jobs_resolves_each_queue_row(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(data_loader, "get_supabase_client", lambda: client)

    ok, message = data_loader.dismiss_discovered_jobs([7, 8])

    assert ok is True
    assert message == "Dismissed 2 job(s)."
    eq_calls = [call for call in client.queries["job_review_queue"].calls if call[0] == "eq"]
    assert eq_calls == [("eq", "id", 7), ("eq", "id", 8)]
