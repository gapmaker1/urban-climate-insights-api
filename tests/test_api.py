from datetime import date


def register_and_login(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123!",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "alice", "password": "Password123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_city(client, headers, name="Leeds"):
    response = client.post(
        "/api/v1/cities",
        json={
            "name": name,
            "country_code": "GB",
            "region": "England",
            "latitude": 53.8,
            "longitude": -1.55,
            "timezone": "Europe/London",
            "source": "test",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_register_login_and_profile(client):
    headers = register_and_login(client)
    profile_response = client.get("/api/v1/auth/me", headers=headers)

    assert profile_response.status_code == 200
    assert profile_response.json()["username"] == "alice"


def test_city_and_record_crud(client):
    headers = register_and_login(client)
    city = create_city(client, headers)

    list_response = client.get("/api/v1/cities")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_city_response = client.put(
        f"/api/v1/cities/{city['id']}",
        json={"region": "West Yorkshire"},
        headers=headers,
    )
    assert update_city_response.status_code == 200
    assert update_city_response.json()["region"] == "West Yorkshire"

    record_response = client.post(
        "/api/v1/records",
        json={
            "city_id": city["id"],
            "record_date": "2026-04-10",
            "temperature_max_c": 17.5,
            "temperature_min_c": 8.1,
            "precipitation_sum_mm": 1.2,
            "wind_speed_max_kmh": 24.5,
            "pm2_5": 7.0,
            "pm10": 11.4,
            "nitrogen_dioxide": 19.2,
            "ozone": 58.0,
            "european_aqi": 31.0,
            "source": "test",
        },
        headers=headers,
    )
    assert record_response.status_code == 201
    record = record_response.json()

    get_record_response = client.get(f"/api/v1/records/{record['id']}")
    assert get_record_response.status_code == 200
    assert get_record_response.json()["city_id"] == city["id"]

    update_record_response = client.put(
        f"/api/v1/records/{record['id']}",
        json={"temperature_max_c": 18.2},
        headers=headers,
    )
    assert update_record_response.status_code == 200
    assert update_record_response.json()["temperature_max_c"] == 18.2

    delete_record_response = client.delete(f"/api/v1/records/{record['id']}", headers=headers)
    assert delete_record_response.status_code == 204

    delete_city_response = client.delete(f"/api/v1/cities/{city['id']}", headers=headers)
    assert delete_city_response.status_code == 204


def test_analytics_endpoints(client):
    headers = register_and_login(client)
    city_one = create_city(client, headers, name="Leeds")
    city_two = create_city(client, headers, name="London")

    city_one_records = [
        ("2026-04-08", 12.0, 5.0, 3.0, 5.0, 25.0),
        ("2026-04-09", 13.0, 6.0, 0.5, 6.0, 28.0),
        ("2026-04-10", 22.0, 9.0, 0.0, 18.0, 70.0),
    ]
    city_two_records = [
        ("2026-04-08", 14.0, 7.0, 1.5, 7.0, 32.0),
        ("2026-04-09", 15.5, 8.0, 0.0, 8.0, 35.0),
        ("2026-04-10", 16.0, 9.0, 0.2, 9.0, 38.0),
    ]

    for record_date, temp_max, temp_min, rain, pm25, aqi in city_one_records:
        client.post(
            "/api/v1/records",
            json={
                "city_id": city_one["id"],
                "record_date": record_date,
                "temperature_max_c": temp_max,
                "temperature_min_c": temp_min,
                "precipitation_sum_mm": rain,
                "wind_speed_max_kmh": 20.0,
                "pm2_5": pm25,
                "pm10": pm25 + 4,
                "nitrogen_dioxide": 20.0,
                "ozone": 55.0,
                "european_aqi": aqi,
                "source": "test",
            },
            headers=headers,
        )

    for record_date, temp_max, temp_min, rain, pm25, aqi in city_two_records:
        client.post(
            "/api/v1/records",
            json={
                "city_id": city_two["id"],
                "record_date": record_date,
                "temperature_max_c": temp_max,
                "temperature_min_c": temp_min,
                "precipitation_sum_mm": rain,
                "wind_speed_max_kmh": 22.0,
                "pm2_5": pm25,
                "pm10": pm25 + 5,
                "nitrogen_dioxide": 18.0,
                "ozone": 52.0,
                "european_aqi": aqi,
                "source": "test",
            },
            headers=headers,
        )

    summary_response = client.get(
        f"/api/v1/analytics/cities/{city_one['id']}/summary",
        params={"start_date": date(2026, 4, 8).isoformat(), "end_date": date(2026, 4, 10).isoformat()},
    )
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["record_count"] == 3
    assert summary["hottest_day"]["record_date"] == "2026-04-10"

    compare_response = client.get(
        "/api/v1/analytics/compare",
        params=[("city_ids", city_one["id"]), ("city_ids", city_two["id"])],
    )
    assert compare_response.status_code == 200
    assert len(compare_response.json()) == 2

    anomalies_response = client.get(
        f"/api/v1/analytics/cities/{city_one['id']}/anomalies",
        params={"metric": "temperature_max_c", "threshold": 1.2},
    )
    assert anomalies_response.status_code == 200
    anomaly_dates = [item["record_date"] for item in anomalies_response.json()["anomalies"]]
    assert "2026-04-10" in anomaly_dates
