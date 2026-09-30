import logging
import os
import signal
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.config.settings import TELEGRAM_BOT_TOKEN, UPLOAD_DIR
from app.parsers.resume_parser import extract_text_from_pdf
from app.services.analyzer import analyze_resume_and_jd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SESSION_DATA = {}

BOT_LOCK_PATH = Path(__file__).resolve().parent.parent.parent / "data" / ".bot.lock"


def _is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False

    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def acquire_single_instance_lock() -> None:
    BOT_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)

    if BOT_LOCK_PATH.exists():
        try:
            existing_pid = int(BOT_LOCK_PATH.read_text(encoding="utf-8").strip())
        except ValueError:
            existing_pid = -1

        if existing_pid > 0 and _is_pid_running(existing_pid):
            raise RuntimeError(
                "Another CareerLens bot instance is already running. "
                "Please stop the existing process before starting a new one."
            )

        BOT_LOCK_PATH.unlink(missing_ok=True)

    BOT_LOCK_PATH.write_text(str(os.getpid()), encoding="utf-8")


def release_single_instance_lock() -> None:
    try:
        BOT_LOCK_PATH.unlink(missing_ok=True)
    except OSError:
        logger.warning("Could not remove bot lock file at startup cleanup.")


def _shutdown_handler(signum, frame):
    release_single_instance_lock()
    raise SystemExit(0)


signal.signal(signal.SIGINT, _shutdown_handler)
signal.signal(signal.SIGTERM, _shutdown_handler)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "👋 Welcome to CareerLens AI!\n\n"
        "I can:\n"
        "📄 Analyze your resume\n"
        "📋 Compare it with a job description\n"
        "🎯 Calculate your match score\n"
        "🧠 Identify skill gaps\n"
        "🎓 Recommend certifications\n"
        "📚 Create a learning roadmap\n\n"
        "Send /analyze to begin."
    )
    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Show commands\n"
        "/analyze - Start resume and JD upload flow"
    )


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    SESSION_DATA[user_id] = {"resume_path": None, "jd_path": None, "resume_text": None, "jd_text": None}
    await update.message.reply_text("✅ Please upload your resume as a PDF file.")


async def reset_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    SESSION_DATA.pop(user_id, None)
    await update.message.reply_text("Session reset. Send /analyze to start again.")


def _is_pdf_document(document) -> bool:
    file_name = (document.file_name or "").lower()
    mime_type = (document.mime_type or "").lower()
    return file_name.endswith(".pdf") or mime_type == "application/pdf"


def _extract_required_text(file_path: Path, document_kind: str) -> str:
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise ValueError(
            f"The {document_kind} PDF contains no selectable text. "
            "Please upload a text-based PDF instead of a scanned image."
        )
    return text


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not update.message or not update.message.document:
        return

    doc = update.message.document
    if not _is_pdf_document(doc):
        await update.message.reply_text("Please upload a PDF file.")
        return

    session = SESSION_DATA.setdefault(user_id, {})
    if session.get("resume_path") is None:
        file_path = UPLOAD_DIR / f"{user_id}_resume.pdf"
        file = await doc.get_file()
        await file.download_to_drive(file_path)

        try:
            text = _extract_required_text(file_path, "resume")
            session["resume_path"] = str(file_path)
            session["resume_text"] = text
            await update.message.reply_text(
                "✅ Resume received.\n\n"
                "Now upload the job description PDF."
            )
        except Exception as exc:
            logger.exception("Failed to extract resume text")
            file_path.unlink(missing_ok=True)
            await update.message.reply_text(f"Failed to read the resume PDF: {exc}")
        return

    if session.get("jd_path") is None:
        file_path = UPLOAD_DIR / f"{user_id}_jd.pdf"
        file = await doc.get_file()
        await file.download_to_drive(file_path)

        try:
            jd_text = _extract_required_text(file_path, "job description")
            session["jd_text"] = jd_text

            resume_text = session.get("resume_text") or ""
            analysis = analyze_resume_and_jd(resume_text, jd_text)
            session["jd_path"] = str(file_path)

            matched = ", ".join(analysis["matched_skills"]) if analysis["matched_skills"] else "None"
            missing = ", ".join(analysis["missing_skills"]) if analysis["missing_skills"] else "None"
            suggestions = "\n".join(analysis["suggestions"]) if analysis["suggestions"] else "- No major gaps found."
            certifications = "\n".join(f"{i+1}. {cert}" for i, cert in enumerate(analysis["certifications"])) if analysis["certifications"] else "- No certification recommendations yet."

            response = (
                "✅ Job description received.\n\n"
                "📊 Resume vs JD Analysis\n"
                f"Overall match score: {analysis['score']}/100\n\n"
                f"Matched skills: {matched}\n"
                f"Missing skills: {missing}\n\n"
                "🧠 Skill gap suggestions:\n"
                f"{suggestions}\n\n"
                "🎓 Recommended certifications:\n"
                f"{certifications}\n\n"
                "💡 Tip: Update your resume to highlight the missing skills and include small project evidence."
            )

            await update.message.reply_text(response)
        except Exception as exc:
            logger.exception("Failed to analyze resume and job description")
            file_path.unlink(missing_ok=True)
            await update.message.reply_text(f"Failed to analyze the documents: {exc}")
        return

    await update.message.reply_text("You already uploaded both documents. Please use /analyze again to reset the session.")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing. Add it to your .env file.")

    try:
        acquire_single_instance_lock()
    except RuntimeError as exc:
        logger.error(str(exc))
        raise SystemExit(1) from exc

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze))
    application.add_handler(CommandHandler("reset", reset_session))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("Starting CareerLens AI Telegram bot...")
    try:
        application.run_polling()
    except Exception:
        release_single_instance_lock()
        raise

    release_single_instance_lock()


if __name__ == "__main__":
    main()
