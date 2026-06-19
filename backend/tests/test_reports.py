def test_admin_dashboard_access_denied_for_infocu(client, mock_user_override):
    # Sisteme infocu olarak giriş yapılmış gibi davran
    mock_user_override(role="infocu")

    # Admin dashboard endpoint'ine istek at
    response = client.get("/api/reports/dashboard?start_date=2026-06-01&end_date=2026-06-30")

    # Sistem 403 hatası vermeli
    assert response.status_code == 403
    assert response.json()["detail"] == "Operation not permitted for your role"

def test_admin_dashboard_access_granted_for_admin(client, mock_user_override):
    # Sisteme admin olarak giriş yapılmış gibi davran
    mock_user_override(role="admin")

    # DB mocklanmadığı için veritabanı sorgusu hata verecektir (500), 
    # ancak önemli olan yetki kontrolünü (403) başarıyla aşmasıdır.
    response = client.get("/api/reports/dashboard?start_date=2026-06-01&end_date=2026-06-30")

    # 403 dönmediğini doğrula
    assert response.status_code != 403