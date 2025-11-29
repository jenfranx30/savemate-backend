"""
Script to grant admin privileges to a user
Usage: python scripts/make_admin.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db, close_db
from app.models.user import User


async def make_admin(email: str):
    """Make a user an admin"""
    print(f"🔍 Searching for user: {email}")
    await init_db()
    
    try:
        user = await User.find_one(User.email == email)
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            print("💡 Available users:")
            all_users = await User.find_all().to_list()
            for u in all_users:
                print(f"   - {u.email} ({u.username})")
            return
        
        if user.is_admin:
            print(f"ℹ️  User {email} is already an admin")
        else:
            user.is_admin = True
            await user.save()
            print(f"✅ Successfully granted admin privileges to {email}")
        
        print(f"\n📋 User Details:")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Admin: {user.is_admin}")
        print(f"   Business Owner: {user.is_business_owner}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await close_db()


async def list_admins():
    """List all admin users"""
    print("👑 Admin Users:")
    await init_db()
    
    try:
        admins = await User.find(User.is_admin == True).to_list()
        
        if not admins:
            print("   No admin users found")
        else:
            for admin in admins:
                print(f"   - {admin.email} ({admin.username})")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await close_db()


async def remove_admin(email: str):
    """Remove admin privileges from a user"""
    print(f"🔍 Searching for user: {email}")
    await init_db()
    
    try:
        user = await User.find_one(User.email == email)
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            return
        
        if not user.is_admin:
            print(f"ℹ️  User {email} is not an admin")
        else:
            user.is_admin = False
            await user.save()
            print(f"✅ Successfully removed admin privileges from {email}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await close_db()


def main():
    """Main function with menu"""
    print("=" * 60)
    print("SaveMate Admin Management")
    print("=" * 60)
    print()
    print("1. Grant admin privileges")
    print("2. Remove admin privileges")
    print("3. List all admins")
    print("4. Exit")
    print()
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == "1":
        email = input("Enter user email: ").strip()
        asyncio.run(make_admin(email))
    elif choice == "2":
        email = input("Enter user email: ").strip()
        asyncio.run(remove_admin(email))
    elif choice == "3":
        asyncio.run(list_admins())
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid option")


if __name__ == "__main__":
    main()