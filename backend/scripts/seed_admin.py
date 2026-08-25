"""
Utility script to seed or create an admin user account.
Usage:
    python scripts/seed_admin.py --email admin@gmail.com --password admin@123 --name "Admin User"
"""

import argparse
import asyncio
import logging
import sys
import uuid

from app.core.security import get_password_hash
from app.db.models.user import User
from app.db.session import AsyncSessionLocal
from app.repositories.user_repository import UserRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_user(email: str, password: str, full_name: str) -> None:
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        existing = await user_repo.get_by_email(email)
        if existing:
            logger.info("User with email %s already exists. Updating password...", email)
            existing.hashed_password = get_password_hash(password)
            existing.is_active = True
            existing.is_superuser = True
            await user_repo.update(existing)
            logger.info("Admin user '%s' password updated successfully!", email)
            return

        hashed_pw = get_password_hash(password)
        new_user = User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hashed_pw,
            full_name=full_name,
            is_active=True,
            is_superuser=True,
        )
        await user_repo.create(new_user)
        logger.info("Admin user '%s' created successfully!", email)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Admin User")
    parser.add_argument("--email", default="admin@gmail.com", help="User email")
    parser.add_argument("--password", default="admin@123", help="User password")
    parser.add_argument("--name", default="Admin", help="User full name")
    args = parser.parse_args()

    try:
        asyncio.run(seed_user(args.email, args.password, args.name))
    except Exception as exc:
        logger.error("Error creating user: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
