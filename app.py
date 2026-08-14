def update_record(
    row_number,
    created_at,
    name,
    mobile,
    service,
    amount,
    payment,
    expiry
):

    payload = {

        "action": "update",

        "row_number": str(row_number),

        "created_at": str(created_at),

        "name": str(name),

        "mobile": str(mobile),

        "service": str(service),

        "amount": str(amount),

        "payment": str(payment),

        "expiry": str(expiry)
    }

    try:

        res = requests.post(
            WEB_APP_URL,
            data=payload,
            timeout=20,
            allow_redirects=True
        )

        if res.status_code >= 400:
            return False

        try:

            result = res.json()

            return result.get(
                "success",
                False
            )

        except Exception:

            return True

    except Exception:

        return False


def delete_record(row_number):

    payload = {

        "action": "delete",

        "row_number": str(row_number)
    }

    try:

        res = requests.post(
            WEB_APP_URL,
            data=payload,
            timeout=20,
            allow_redirects=True
        )

        if res.status_code >= 400:
            return False

        try:

            result = res.json()

            return result.get(
                "success",
                False
            )

        except Exception:

            return True

    except Exception:

        return False
