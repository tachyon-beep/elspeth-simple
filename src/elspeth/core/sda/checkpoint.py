"""Checkpoint management for resumable SDA execution."""

from __future__ import annotations

from pathlib import Path


class CheckpointManager:
    """Manages checkpoint state for resumable processing."""

    def __init__(self, checkpoint_path: Path | str, field: str):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_path: Path to checkpoint file (plain text, one ID per line)
            field: Field name containing unique row ID (currently unused, reserved for future use)
        """
        self.checkpoint_path = Path(checkpoint_path)
        self.field = field  # Reserved for future use (e.g., validating field exists in data)
        self._processed_ids: set[str] = self._load_checkpoint()

    def _load_checkpoint(self) -> set[str]:
        """Load processed IDs from checkpoint file."""
        if not self.checkpoint_path.exists():
            return set()

        processed_ids = set()
        with self.checkpoint_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                processed_ids.add(line)
        return processed_ids

    def is_processed(self, row_id: str) -> bool:
        """Check if row ID has been processed."""
        return row_id in self._processed_ids

    def mark_processed(self, row_id: str) -> None:
        """Mark row ID as processed and append to checkpoint."""
        if row_id in self._processed_ids:
            return

        self._processed_ids.add(row_id)
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        with self.checkpoint_path.open("a", encoding="utf-8") as f:
            f.write(f"{row_id}\n")
