import random

class ScrapingIdentity:
    """Gera identidades completas e coerentes para evitar detecção."""
    
    IDENTITIES = [
        {
            # Identidade 1: Chrome no Windows (O mais comum)
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "headers": {
                "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            }
        },
        {
            # Identidade 2: Edge no Windows (Muito comum em ambientes corporativos)
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
            "headers": {
                "sec-ch-ua": '"Chromium";v="122", "Microsoft Edge";v="122", "Not:A-Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            }
        },
        {
            # Identidade 3: Chrome no macOS (Perfil de investidor de alta renda)
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "headers": {
                "sec-ch-ua": '"Chromium";v="121", "Google Chrome";v="121", "Not:A-Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
            }
        }
    ]

    @classmethod
    def get_full_identity(cls):
        """Retorna User-Agent e Headers baseados na mesma plataforma."""
        identity = random.choice(cls.IDENTITIES)
        
        base_headers = {
            "User-Agent": identity["user_agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }
        
        # Mescla os headers específicos da plataforma (sec-ch-ua)
        base_headers.update(identity["headers"])
        return base_headers