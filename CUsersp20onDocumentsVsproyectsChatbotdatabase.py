def create_advisor_request(name: str, email: str, phone: Optional[str], message: str) -> int:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO advisor_requests (name, email, phone, message) VALUES (?, ?, ?, ?)",
        (name, email, phone, message)
    )
    request_id = c.lastrowid
    conn.commit()
    conn.close()
    return request_id
