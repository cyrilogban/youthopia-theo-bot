from datetime import datetime
from typing import List, Dict
from theo.infra.google_calendar_client import GoogleCalendarClient

class CalendarService:
    def __init__(self, client: GoogleCalendarClient, calendar_ids: List[str]):
        self.client = client
        self.calendar_ids = calendar_ids

    def generate_daily_summary(self) -> str:
        """Fetches today's events from all calendars and formats them as a readable string."""
        all_events = []
        errors = []

        for cal_id in self.calendar_ids:
            try:
                events = self.client.get_events_for_today(cal_id)
                all_events.extend(events)
            except Exception as e:
                errors.append(f"Could not fetch calendar {cal_id}: {str(e)}")

        if not all_events:
            msg = "📅 No events scheduled for today. Enjoy your free time! 🌿"
            if errors:
                msg += "\n\n⚠️ *Some errors occurred:* \n" + "\n".join(errors)
            return msg

        # Sort aggregated events by start time
        # All-day events (date only) will appear before timed events (dateTime)
        all_events.sort(key=lambda x: x['start'].get('dateTime', x['start'].get('date')))

        summary_lines = ["📅 *Your Schedule for Today:*"]
        
        for event in all_events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event.get('end', {}).get('dateTime', event.get('end', {}).get('date'))
            summary = event.get('summary', 'No Title')
            
            if 'T' in start:
                # Timed event
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                start_str = start_dt.strftime("%I:%M %p")
                
                if end and 'T' in end:
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    end_str = end_dt.strftime("%I:%M %p")
                    summary_lines.append(f"🔹 {start_str} - {end_str} - {summary}")
                else:
                    summary_lines.append(f"🔹 {start_str} - {summary}")
            else:
                # All-day event
                summary_lines.append(f"🔹 [All Day] {summary}")

        if errors:
            summary_lines.append("\n⚠️ *Note: Some calendars could not be reached:*")
            for err in errors:
                summary_lines.append(f"• {err}")

        summary_lines.append("\nHave a productive day! 🚀")
        return "\n".join(summary_lines)
