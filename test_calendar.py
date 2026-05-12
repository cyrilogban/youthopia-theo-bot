import os
from dotenv import load_dotenv
from theo.app.config import load_settings
from theo.infra.google_calendar_client import GoogleCalendarClient
from theo.core.services.calendar_service import CalendarService

def test_calendar():
    print("🚀 Starting Calendar Test...")
    
    try:
        # 1. Load settings
        settings = load_settings()
        print(f"✅ Settings loaded. Calendar IDs: {', '.join(settings.google_calendar_ids)}")
        
        # 2. Initialize Client
        client = GoogleCalendarClient(creds_path=settings.google_creds_path)
        
        # 3. Initialize Service
        service = CalendarService(client=client, calendar_ids=settings.google_calendar_ids)
        
        # 4. Generate Summary
        print("📡 Fetching events from Google...")
        summary = service.generate_daily_summary()
        
        print("\n--- TEST RESULT ---")
        print(summary)
        print("-------------------\n")
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    test_calendar()
