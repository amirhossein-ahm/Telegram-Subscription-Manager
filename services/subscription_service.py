import secrets
import base64

from models import Channel, Subscription, db_session

from services.telegram_service import telegram_service

from services.extractor_service import extractor_service


class SubscriptionService:

    @staticmethod
    def generate_token():

        return secrets.token_urlsafe(32)

    def create_subscription(self, name, channel_ids, remark_name="", base64_enabled=True):

        try:
            channel_ids = [int(channel_id) for channel_id in channel_ids]
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid channel selection") from exc

        if not channel_ids:
            raise ValueError("Select at least one channel")

        channel_ids = sorted(set(channel_ids))

        with db_session() as db:
            subscription = Subscription(
                name=name,
                remark_name=remark_name or None,
                token=self.generate_token(),
                base64_enabled=base64_enabled,
            )

            channels = db.query(Channel).filter(Channel.id.in_(channel_ids)).all()

            if len(channels) != len(channel_ids):
                raise ValueError("One or more selected channels do not exist")

            subscription.channels.extend(channels)

            db.add(subscription)

            db.commit()

            return subscription.id

    def delete_subscription(self, subscription_id):

        with db_session() as db:
            sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()

            if not sub:
                return False

            db.delete(sub)

            db.commit()

            return True

    def get_subscription(self, subscription_id):

        with db_session() as db:
            return db.query(Subscription).filter(Subscription.id == subscription_id).first()

    def get_subscription_by_token(self, token):

        with db_session() as db:
            return db.query(Subscription).filter(Subscription.token == token).first()

    def get_feed_settings(self, token):

        with db_session() as db:
            subscription = db.query(Subscription).filter(Subscription.token == token).first()

            if not subscription:
                return None

            return {
                "id": subscription.id,
                "base64_enabled": subscription.base64_enabled,
            }

    def get_all_subscriptions(self):

        with db_session() as db:
            return db.query(Subscription).all()

    async def build_subscription(self, subscription_id):

        with db_session() as db:
            subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()

            if not subscription:

                raise ValueError("Subscription not found")

            remark_name = subscription.remark_name

            channels = [
                (channel.name, channel.message_limit)
                for channel in subscription.channels
                if channel.enabled
            ]

        configs = []

        for channel_name, message_limit in channels:
            messages = await telegram_service.get_messages(channel_name, message_limit)

            extracted = extractor_service.extract_from_messages(messages)

            configs.extend(extracted)

        configs = extractor_service.deduplicate(configs)

        if remark_name:
            configs = [extractor_service.rewrite_remark(cfg, remark_name) for cfg in configs]

        return configs

    async def build_plain_text(self, subscription_id):

        configs = await self.build_subscription(subscription_id)

        return "\n".join(configs)

    async def build_base64(self, subscription_id):

        content = await self.build_plain_text(subscription_id)

        return base64.b64encode(content.encode("utf-8")).decode("utf-8")

    async def build_feed(self, subscription_id, base64_enabled):

        if base64_enabled:
            return await self.build_base64(subscription_id)

        return await self.build_plain_text(subscription_id)


subscription_service = SubscriptionService()
