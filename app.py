# ====================================================
# SAVE EDITED DATA
# ====================================================

if st.button(
    "💾 Save Changes to Google Sheet",
    type="primary",
    use_container_width=True
):

    changes_found = False
    errors = []

    for index in range(len(edited_df)):

        original = editable_df.iloc[index]
        edited = edited_df.iloc[index]

        changed = False

        for column in editable_df.columns:

            old_value = str(
                original[column]
            ).strip()

            new_value = str(
                edited[column]
            ).strip()

            if old_value != new_value:
                changed = True
                break

        if not changed:
            continue

        changes_found = True

        # ------------------------------------------------
        # GET ORIGINAL GOOGLE SHEET ROW NUMBER SAFELY
        # ------------------------------------------------

        if "_row_number" in df_all.columns:

            row_number = df_all.iloc[index][
                "_row_number"
            ]

        else:

            # Sheet row 1 = Header
            # Therefore first data row = 2
            row_number = index + 2

        try:

            row_number = int(
                float(row_number)
            )

        except Exception:

            row_number = index + 2


        # ------------------------------------------------
        # UPDATE PAYLOAD
        # ------------------------------------------------

        update_payload = {

            "action": "update",

            "row_number": str(
                row_number
            ),

            "created_at": str(
                edited["created_at"]
            ).strip(),

            "name": str(
                edited["name"]
            ).strip(),

            "mobile": str(
                edited["mobile"]
            ).strip(),

            "service": str(
                edited["service"]
            ).strip(),

            "amount": str(
                edited["amount"]
            ).strip(),

            "payment": str(
                edited["payment"]
            ).strip(),

            "expiry": str(
                edited["expiry"]
            ).strip()
        }


        # ------------------------------------------------
        # SEND UPDATE
        # ------------------------------------------------

        success, message = send_to_google(
            update_payload
        )


        if not success:

            errors.append(
                f"Row {row_number}: {message}"
            )


    # ====================================================
    # RESULT
    # ====================================================

    if not changes_found:

        st.info(
            "ℹ️ No changes detected."
        )

    elif errors:

        st.error(
            "❌ Some changes could not be saved."
        )

        for error in errors:

            st.error(error)

    else:

        st.session_state.success_message = (
            "✅ Customer data updated successfully!"
        )

        st.rerun()
