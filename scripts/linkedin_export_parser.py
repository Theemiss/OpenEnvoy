#!/usr/bin/env python3
"""Script to parse LinkedIn data export."""

import asyncio
import argparse
import sys
from pathlib import Path
from pprint import pprint

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.ingestion.linkedin.exporter_parser import LinkedInExportParser
from backend.core.database import db_manager


async def parse_export(export_path: str, profile_id: int = None):
    """Parse LinkedIn export and optionally import to profile."""
    
    parser = LinkedInExportParser(Path(export_path))
    
    print(f"📂 Parsing LinkedIn export from: {export_path}")
    print("=" * 50)
    
    # Parse the data
    data = await parser.parse()
    
    # Print summary
    print("\n📊 Export Summary:")
    print(f"  Profile: {data['profile'].get('current_title', 'N/A')}")
    print(f"  Connections: {len(data['connections'])}")
    print(f"  Positions: {len(data['positions'])}")
    print(f"  Education: {len(data['education'])}")
    print(f"  Skills: {len(data['skills'])}")
    print(f"  Recommendations: {len(data['recommendations'])}")
    print(f"  Messages: {len(data['messages'])}")
    
    # Show sample data
    if data['positions']:
        print("\n💼 Recent Positions:")
        for pos in data['positions'][:3]:
            print(f"  • {pos['title']} at {pos['company']}")
    
    if data['skills']:
        print("\n🔧 Top Skills:")
        for skill in data['skills'][:5]:
            print(f"  • {skill['name']} ({skill.get('endorsements', 0)} endorsements)")
    
    # Import to profile if requested
    if profile_id:
        print(f"\n📥 Importing to profile {profile_id}...")
        await db_manager.initialize()
        
        try:
            result = await parser.import_to_profile(profile_id)
            print(f"✅ Import complete:")
            print(f"  • Positions added: {result['positions_added']}")
            print(f"  • Education added: {result['education_added']}")
            print(f"  • Skills added: {result['skills_added']}")
        finally:
            await db_manager.close()
    
    return data


async def list_profiles():
    """List available profiles."""
    await db_manager.initialize()
    
    try:
        from backend.models.profile import Profile
        from sqlalchemy import select
        
        async with db_manager.session() as session:
            result = await session.execute(select(Profile))
            profiles = result.scalars().all()
            
            print("\n👤 Available Profiles:")
            for profile in profiles:
                print(f"  ID: {profile.id} - {profile.full_name} ({profile.title})")
    finally:
        await db_manager.close()


def main():
    parser = argparse.ArgumentParser(description="Parse LinkedIn data export")
    parser.add_argument("export_path", help="Path to LinkedIn export (ZIP or directory)")
    parser.add_argument("--profile-id", type=int, help="Import to profile ID")
    parser.add_argument("--list-profiles", action="store_true", help="List available profiles")
    
    args = parser.parse_args()
    
    if args.list_profiles:
        asyncio.run(list_profiles())
    elif args.export_path:
        asyncio.run(parse_export(args.export_path, args.profile_id))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()