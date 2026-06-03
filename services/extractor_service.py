import base64
import binascii
import re
from html import unescape
from urllib.parse import urlparse, unquote


SUPPORTED_PROTOCOLS = {
    "vless",
    "vmess",
    "trojan",
    "ss",
    "ssr",
    "hy2",
    "hysteria",
    "hysteria2",
    "tuic",
}

CONFIG_PATTERN = re.compile(
    r"\b(?:vless|vmess|trojan|ss|ssr|hy2|hysteria|hysteria2|tuic)://[^\s<>\"'`]+",
    re.IGNORECASE,
)
BASE64_PATTERN = re.compile(r"^[A-Za-z0-9+/_-]+={0,2}$")
COUNTRY_EMOJI_PATTERN = re.compile(r"[\U0001F1E6-\U0001F1FF]{2}")
SS_METHOD_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
TRAILING_PUNCTUATION = ".,;)]}"


class ExtractorService:
    @staticmethod
    def clean_text(text: str) -> str:
        return unescape(text or "")

    @staticmethod
    def protocol(config: str) -> str | None:
        if "://" not in config:
            return None
        return config.split("://", 1)[0].lower()

    def normalize(self, config: str) -> str:
        config = config.strip()
        while config.endswith(tuple(TRAILING_PUNCTUATION)):
            config = config[:-1]

        return config.strip()

    @staticmethod
    def decode_base64_payload(payload: str) -> str | None:
        if not payload or not BASE64_PATTERN.match(payload):
            return None

        try:
            padded = payload + "=" * ((4 - len(payload) % 4) % 4)
            decoded = base64.b64decode(padded, altchars=b"-_", validate=True)
            return decoded.decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            return None

    def validate_vmess(self, config: str) -> bool:
        payload = config.split("://", 1)[1]
        return self.decode_base64_payload(payload) is not None

    @staticmethod
    def validate_ss_credentials(credentials: str) -> bool:
        if not credentials or "\ufffd" in credentials or ":" not in credentials:
            return False

        method, password = credentials.split(":", 1)
        return bool(method and password and SS_METHOD_PATTERN.match(method))

    def validate_ss(self, config: str) -> bool:
        try:
            parsed = urlparse(config)
            if parsed.scheme.lower() != "ss":
                return False

            if parsed.hostname and parsed.port:
                if parsed.password is not None:
                    credentials = f"{unquote(parsed.username or '')}:{unquote(parsed.password)}"
                else:
                    credentials = self.decode_base64_payload(parsed.username or "")

                return self.validate_ss_credentials(credentials or "")

            payload = config.split("://", 1)[1].split("#", 1)[0].split("?", 1)[0]
            decoded = self.decode_base64_payload(payload)
            if not decoded or "@" not in decoded:
                return False

            credentials, server = decoded.rsplit("@", 1)
            server_parsed = urlparse("//" + server)
            return self.validate_ss_credentials(credentials) and bool(
                server_parsed.hostname and server_parsed.port
            )
        except ValueError:
            return False

    @staticmethod
    def validate_url(config: str) -> bool:
        try:
            parsed = urlparse(config)
            return bool(parsed.scheme and parsed.netloc)
        except ValueError:
            return False

    def validate(self, config: str) -> bool:
        proto = self.protocol(config)
        if proto not in SUPPORTED_PROTOCOLS:
            return False

        if proto == "vmess":
            return self.validate_vmess(config)
        if proto == "ss":
            return self.validate_ss(config)

        return self.validate_url(config)

    def extract_from_text(self, text: str) -> list[str]:
        results = []
        for match in CONFIG_PATTERN.finditer(self.clean_text(text)):
            config = self.normalize(match.group(0))
            if self.validate(config):
                results.append(config)

        return results

    def extract_from_messages(self, messages) -> list[str]:
        configs = []
        for message in messages:
            configs.extend(self.extract_from_text(message))
        return self.deduplicate(configs)

    @staticmethod
    def deduplicate(configs) -> list[str]:
        seen = set()
        output = []
        for config in configs:
            if config in seen:
                continue
            seen.add(config)
            output.append(config)
        return output

    def group_by_protocol(self, configs) -> dict[str | None, list[str]]:
        grouped = {}
        for config in configs:
            grouped.setdefault(self.protocol(config), []).append(config)
        return grouped

    def rewrite_remark(self, config: str, custom_name: str) -> str:
        if not custom_name:
            return config

        if "#" not in config:
            return f"{config}#{custom_name}"

        base, remark = config.split("#", 1)
        flags = COUNTRY_EMOJI_PATTERN.findall(unquote(remark))
        if flags:
            return f"{base}#{flags[0]} {custom_name}"

        return f"{base}#{custom_name}"


extractor_service = ExtractorService()
