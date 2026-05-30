def _generate_unique_service_id(self) -> str:
        """
        Generate a unique service ID with collision check
        
        Returns:
            Unique service ID in format SVC-XXXXXXXX
        """
        max_attempts = 10
        for _ in range(max_attempts):
            service_id = f"SVC-{uuid.uuid4().hex[:8].upper()}"
            existing = self.get_service_by_id(service_id)
            if not existing:
                return service_id
        
        # Fallback to full UUID if collision persists
        return f"SVC-{uuid.uuid4().hex.upper()}"