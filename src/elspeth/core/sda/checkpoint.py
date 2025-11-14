"""Checkpoint management for resumable SDA execution."""

from __future__ import annotations

from pathlib import Path
from typing import Set


class CheckpointManager:
    """Manages checkpoint state for resumable processing."""

    def __init__(self, checkpoint_path: Path | str, field: str):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_path: Path to checkpoint JSONL file
            field: Field name containing unique row ID
        """
        self.checkpoint_path = Path(checkpoint_path)
        self.field = field
        self._processed_ids: Set[str] = self._load_checkpoint()

    def _load_checkpoint(self) -> Set[str]:
        """Load processed IDs from checkpoint file."""
        if not self.checkpoint_path.exists():
            return set()

        processed_ids = set()
        with open(self.checkpoint_path, "r") as f:
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

        with open(self.checkpoint_path, "a") as f:
            f.write(f"{row_id}\n")
