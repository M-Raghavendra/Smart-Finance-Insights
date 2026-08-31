from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import date
import calendar

from services.report_service import (
    parse_month_year,
    get_monthly_financial_report,
    get_goal_progress_report,
    generate_pdf_report,
    generate_docx_report,
    generate_excel_report
)

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports", methods=["GET"])
@login_required
def view_reports():
    """
    Renders the Financial Reports dashboard page with dynamic Month & Year filtering.
    """
    today = date.today()
    month_param = request.args.get("month")
    year_param = request.args.get("year")

    month, year = parse_month_year(month_param, year_param)

    monthly_report = get_monthly_financial_report(current_user.id, month, year)
    goal_report = get_goal_progress_report(current_user.id)

    months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years_list = list(range(today.year - 5, today.year + 6))

    return render_template(
        "reports.html",
        monthly_report=monthly_report,
        goal_report=goal_report,
        selected_month=month,
        selected_year=year,
        months_list=months_list,
        years_list=years_list
    )


@reports_bp.route("/reports/export/pdf", methods=["GET"])
@login_required
def export_pdf():
    """
    Generates and downloads a PDF financial report for the authenticated user.
    """
    month_param = request.args.get("month")
    year_param = request.args.get("year")
    month, year = parse_month_year(month_param, year_param)

    monthly_report = get_monthly_financial_report(current_user.id, month, year)
    goal_report = get_goal_progress_report(current_user.id)

    pdf_buffer = generate_pdf_report(current_user.full_name, monthly_report, goal_report)

    filename = f"FinSight_Financial_Report_{year}_{month:02d}.pdf"

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )


@reports_bp.route("/reports/export/docx", methods=["GET"])
@login_required
def export_docx():
    """
    Generates and downloads a Word (DOCX) financial report for the authenticated user.
    """
    month_param = request.args.get("month")
    year_param = request.args.get("year")
    month, year = parse_month_year(month_param, year_param)

    monthly_report = get_monthly_financial_report(current_user.id, month, year)
    goal_report = get_goal_progress_report(current_user.id)

    docx_buffer = generate_docx_report(current_user.full_name, monthly_report, goal_report)

    filename = f"FinSight_Financial_Report_{year}_{month:02d}.docx"

    return send_file(
        docx_buffer,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=filename
    )


@reports_bp.route("/reports/export/excel", methods=["GET"])
@login_required
def export_excel():
    """
    Generates and downloads a multi-sheet Excel (XLSX) financial workbook for the authenticated user.
    """
    month_param = request.args.get("month")
    year_param = request.args.get("year")
    month, year = parse_month_year(month_param, year_param)

    monthly_report = get_monthly_financial_report(current_user.id, month, year)
    goal_report = get_goal_progress_report(current_user.id)

    excel_buffer = generate_excel_report(current_user.full_name, monthly_report, goal_report)

    filename = f"FinSight_Financial_Report_{year}_{month:02d}.xlsx"

    return send_file(
        excel_buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )
