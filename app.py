
from pathlib import Path
import pandas as pd
import streamlit as st
from src.predict import predict_transaction
from uuid import uuid4

from src.transaction_log import (
    log_transaction,
    load_transaction_history,
    save_transaction_history
)

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="AI Fraud Detection",
    page_icon="🔍",
    layout="wide"
)


st.sidebar.title("🛡️ Fraud Monitor")
st.sidebar.caption("AI Transaction Risk System")

page = st.sidebar.radio(
    "Navigation",
    [
        "Analyze Transaction",
        "Monitoring Dashboard",
        "Transaction History"
    ],
    key="main_navigation"
)


st.title("🔍 AI Fraud Detection System")
st.write(
    "Enter transaction details to assess potential money-laundering risk."
)

st.warning(
    "Educational prototype using synthetic data. "
    "Predictions are not verified for real-world banking decisions."
)

# -----------------------------
# Transaction input form
# -----------------------------
currencies = [
    "Australian Dollar", "Bitcoin", "Brazil Real",
    "Canadian Dollar", "Euro", "Mexican Peso", "Ruble",
    "Rupee", "Saudi Riyal", "Shekel", "Swiss Franc",
    "UK Pound", "US Dollar", "Yen", "Yuan"
]

payment_formats = [
    "ACH", "Bitcoin", "Cash", "Cheque",
    "Credit Card", "Reinvestment", "Wire"
]
if page == "Analyze Transaction":
    st.subheader("Transaction details")

    with st.form("transaction_form"):
        col1, col2 = st.columns(2)

        with col1:
            amount_received = st.number_input(
                "Amount received",
                min_value=0.01,
                value=1000.0,
                step=100.0
        )

            receiving_currency = st.selectbox(
                "Receiving currency", currencies
        )

            payment_format = st.selectbox(
                "Payment format", payment_formats
        )

            transaction_hour = st.slider(
                "Transaction hour", 0, 23, 12
        )

        with col2:
            amount_paid = st.number_input(
                "Amount paid",
                min_value=0.01,
                value=1000.0,
                step=100.0
        )

            payment_currency = st.selectbox(
                "Payment currency", currencies
        )

            day_of_week = st.selectbox(
                "Day of week (Monday = 0)", list(range(7))
        )

            is_weekend = st.selectbox(
                "Is it a weekend?", [0, 1],
                format_func=lambda value: "Yes" if value == 1 else "No"
        )

        submitted = st.form_submit_button(
            "Analyze transaction",
            type="primary"
    )

# -----------------------------
# Prediction
    # -----------------------------
    if submitted:
        if amount_received <= 0 or amount_paid <= 0:
            st.error("Amounts must be greater than zero.")
        else:
            transaction = {
                "transaction_hour": transaction_hour,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "log_amount_received": __import__("math").log1p(
                    amount_received
                ),
                "log_amount_paid": __import__("math").log1p(
                    amount_paid
                ),
                "currency_mismatch": int(
                    receiving_currency != payment_currency
                ),
                "Receiving Currency": receiving_currency,
                "Payment Currency": payment_currency,
                "Payment Format": payment_format
            }

            try:
                result = predict_transaction(transaction)
                log_transaction(
                    transaction,
                    result,
                    amount_received,
                    amount_paid
                )

                probability = result["fraud_probability"]

                st.subheader("Analysis result")

                metric_col1, metric_col2 = st.columns(2)

                with metric_col1:
                    st.metric(
                        "Estimated laundering score",
                        f"{probability:.1%}"
                    )

                with metric_col2:
                    st.metric(
                        "Decision threshold",
                        "40%"
                    )

                st.progress(min(max(probability, 0.0), 1.0))

                if result["prediction"] == 1:
                    st.error(
                        "⚠️ Flagged for review: the model's score "
                        "meets or exceeds the experimental threshold."
                    )
                else:
                    st.success(
                        "No alert at the current threshold. "
                        "This does not guarantee the transaction is legitimate."
                    )

                st.caption(
                    "This score is a model output, not a confirmed probability "
                    "of criminal activity. Review all decisions independently."
                )

            except Exception as error:
                st.error(f"Prediction failed: {error}")
                st.info(
                    "Check that the saved model exists and that the input "
                    "features match those used during training."
                )

    
elif page == "Monitoring Dashboard":
    st.divider()
    st.header("📊 Transaction Monitoring Dashboard")

    history = load_transaction_history()


    if history.empty:
        st.info(
            "No transactions available yet. "
            "Analyze a transaction to begin monitoring."
        )
    else:
        total_transactions = len(history)

        flagged_transactions = int(
            (history["prediction"] == 1).sum()
        )

        flag_rate = (
            flagged_transactions / total_transactions
        ) * 100

        average_score = (
            history["fraud_probability"].mean() * 100
        )

        # Dashboard metrics
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Transactions Analyzed",
            f"{total_transactions:,}"
        )

        col2.metric(
            "Flagged for Review",
            f"{flagged_transactions:,}"
        )

        col3.metric(
            "Flag Rate",
            f"{flag_rate:.1f}%"
        )

        col4.metric(
            "Average Model Score",
            f"{average_score:.1f}%"
        )

        
        # Risk category breakdown
        st.divider()
        st.subheader("Risk Category Breakdown")

        low_count = int(
            (history["risk_level"] == "Low").sum()
        )

        medium_count = int(
            (history["risk_level"] == "Medium").sum()
        )

        high_count = int(
            (history["risk_level"] == "High").sum()
        )

        risk_col1, risk_col2, risk_col3 = st.columns(3)

        risk_col1.metric("🟢 Low Risk", low_count)
        risk_col2.metric("🟡 Medium Risk", medium_count)
        risk_col3.metric("🔴 High Risk", high_count)

        
        # Risk distribution chart
        st.subheader("Risk Distribution")

        risk_distribution = pd.Series(
            {
                "Low Risk": low_count,
                "Medium Risk": medium_count,
                "High Risk": high_count,
            }
        )

        st.bar_chart(risk_distribution)

        st.caption(
            "Risk categories are based on experimental model-score "
            "thresholds and are intended for demonstration only."
        )



        # Alert breakdown chart
        st.subheader("Transaction Alert Breakdown")

        alert_counts = (
            history["prediction"]
            .map({0: "Not Flagged", 1: "Flagged for Review"})
            .value_counts()
            .reindex(
                ["Not Flagged", "Flagged for Review"],
                fill_value=0
            )
        )

        st.bar_chart(alert_counts)

        
        # Additional alert insights
        st.divider()
        st.subheader("🔎 Alert Insights")

        flagged_history = history[
            history["prediction"] == 1
        ].copy()

        col1, col2 = st.columns(2)

        if flagged_history.empty:
            col1.metric("Highest Estimated Risk Score", "N/A")
            col2.metric("Most Common Payment Format", "N/A")
        else:
            highest_score = (
                flagged_history["fraud_probability"].max() * 100
            )

            most_common_format = (
                flagged_history["payment_format"].mode()
            )

            col1.metric(
                "Highest Estimated Risk Score",
                f"{highest_score:.2f}%"
            )

            col2.metric(
                "Most Common Payment Format",
                most_common_format.iloc[0]
                if not most_common_format.empty
                else "N/A"
            )

        # Recent transaction activity
        st.subheader("📈 Recent Transaction Activity")

        recent_history = history.copy()
        recent_history["timestamp"] = pd.to_datetime(
            recent_history["timestamp"],
            errors="coerce",
            utc=True
        )

        recent_history = recent_history.dropna(
            subset=["timestamp"]
        )

        if recent_history.empty:
            st.info("No valid transaction timestamps available.")
        else:
            recent_history["analysis_date"] = (
                recent_history["timestamp"].dt.date
            )

            daily_activity = (
                recent_history.groupby("analysis_date")
                .size()
                .rename("Transactions Analyzed")
            )

            st.line_chart(daily_activity)

        
        # Flagged transactions table
        st.divider()
        st.subheader("🚨 Flagged Transactions for Review")

        flagged_history = history[
            history["prediction"] == 1
        ].copy()

        if flagged_history.empty:
            st.success(
                "No transactions are currently flagged for review."
            )
        else:
            # Convert scores to percentages for display
            flagged_history["fraud_probability"] = (
                flagged_history["fraud_probability"] * 100
            ).round(2)

            # Payment format filter
            payment_options = sorted(
                flagged_history["payment_format"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_formats = st.multiselect(
                "Filter by payment format",
                options=payment_options,
                default=payment_options,
                key="flagged_payment_format_filter"
            )

            # Risk score filter
            min_score = float(
                flagged_history["fraud_probability"].min()
            )
            max_score = float(
                flagged_history["fraud_probability"].max()
            )

            score_range = st.slider(
                "Estimated risk score range (%)",
                min_value=min_score,
                max_value=max_score,
                value=(min_score, max_score),
                key="flagged_risk_score_filter"
            ) if min_score < max_score else None

            # Apply filters
            filtered_history = flagged_history[
                flagged_history["payment_format"].isin(
                    selected_formats
                )
            ].copy()

            if score_range is not None:
                filtered_history = filtered_history[
                    filtered_history["fraud_probability"].between(
                        score_range[0],
                        score_range[1]
                    )
                ]

            st.caption(
                f"Showing {len(filtered_history)} of "
                f"{len(flagged_history)} flagged transactions"
            )

            # Display selected columns
            display_history = filtered_history.rename(
                columns={
                    "timestamp": "Time Analyzed",
                    "amount_received": "Amount Received",
                    "amount_paid": "Amount Paid",
                    "receiving_currency": "Receiving Currency",
                    "payment_currency": "Payment Currency",
                    "payment_format": "Payment Format",
                    "fraud_probability": "Estimated Risk Score (%)",
                    "risk_level": "Risk Level",
                }
            )

            st.dataframe(
                display_history[
                    [
                        "Time Analyzed",
                        "Amount Received",
                        "Receiving Currency",
                        "Amount Paid",
                        "Payment Currency",
                        "Payment Format",
                        "Estimated Risk Score (%)",
                        "Risk Level",
                    ]
                ].sort_values(
                    "Estimated Risk Score (%)",
                    ascending=False
                ),
                use_container_width=True,
                hide_index=True
            )

            
            # Download flagged transactions report
            if not filtered_history.empty:
                report_columns = [
                    "timestamp",
                    "amount_received",
                    "amount_paid",
                    "receiving_currency",
                    "payment_currency",
                    "payment_format",
                    "fraud_probability",
                    "risk_level",
                ]

                report = filtered_history[report_columns].copy()

                report = report.rename(
                    columns={
                        "timestamp": "Time Analyzed",
                        "amount_received": "Amount Received",
                        "amount_paid": "Amount Paid",
                        "receiving_currency": "Receiving Currency",
                        "payment_currency": "Payment Currency",
                        "payment_format": "Payment Format",
                        "fraud_probability": "Estimated Risk Score (%)",
                        "risk_level": "Risk Level",
                    }
                )

                st.download_button(
                    label="📥 Download Flagged Transactions Report",
                    data=report.to_csv(index=False).encode("utf-8"),
                    file_name="flagged_transactions_report.csv",
                    mime="text/csv",
                    key="download_flagged_report"
                )



elif page == "Transaction History":
    st.divider()
    st.subheader("Transaction History")

    history = load_transaction_history()

    if not history.empty:
        # Ensure investigation status exists.
        if "investigation_status" not in history.columns:
            history["investigation_status"] = "New"
        else:
            history["investigation_status"] = (
                history["investigation_status"].fillna("New")
            )

        # Ensure investigation notes exist.
        if "investigation_notes" not in history.columns:
            history["investigation_notes"] = ""
        else:
            history["investigation_notes"] = (
                history["investigation_notes"].fillna("")
            )
        # Assign permanent IDs to older records that lack them.
        if "transaction_id" not in history.columns:
            history["transaction_id"] = [
                f"TXN-{uuid4().hex[:12].upper()}"
                for _ in range(len(history))
            ]
        else:
            missing_ids = (
                history["transaction_id"].isna()
                | history["transaction_id"].astype(str).str.strip().eq("")
            )

            for i in history.index[missing_ids]:
                history.loc[i, "transaction_id"] = (
                    f"TXN-{uuid4().hex[:12].upper()}"
                )
        # Save IDs and existing data so IDs persist.
        history_to_save = history.drop_duplicates(
            subset=["transaction_id"]
        )
        save_transaction_history(history_to_save)
        history = history_to_save

    if history.empty:
        st.info("No transactions have been logged yet.")
    else:
        st.metric("Transactions analyzed", len(history))

        alerts = history[history["prediction"] == 1]
        st.metric("Transactions flagged for review", len(alerts))

        st.dataframe(
            history.sort_values("timestamp", ascending=False),
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
            "Download transaction history",
            data=history.to_csv(index=False).encode("utf-8"),
            file_name="transaction_history.csv",
            mime="text/csv",
            key="download_transaction_history"
        )
       

        # Investigation notes editor
        st.divider()
        st.subheader("Investigation Notes")

        selected_notes_id = st.selectbox(
            "Select transaction for notes",
            options=history["transaction_id"].tolist(),
            key="selected_notes_transaction_id"
        )

        selected_notes_row = history[
            history["transaction_id"] == selected_notes_id
        ].iloc[0]

        current_notes = selected_notes_row["investigation_notes"]

        new_notes = st.text_area(
            "Record investigation findings or actions",
            value=current_notes,
            placeholder=(
                "Example: Reviewed the transaction. "
                "Requested supporting documents."
            ),
            height=150,
            key=f"notes_editor_{selected_notes_id}"
        )

        if st.button("Save Investigation Notes"):
            history.loc[
                history["transaction_id"] == selected_notes_id,
                "investigation_notes"
            ] = new_notes

            save_transaction_history(history)

            st.success(
                f"Investigation notes saved for transaction "
                f"{selected_notes_id}."
            )
            st.rerun()

    
