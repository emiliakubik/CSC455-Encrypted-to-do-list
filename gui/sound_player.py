from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path

from gui.qt_compat import QtCore, QtMultimedia


class SoundPlayer:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        sound_dir = base_dir / "sound"
        if not sound_dir.exists():
            sound_dir = base_dir / "sounds"
        self._sound_dir = sound_dir if sound_dir.exists() else None
        self._players: dict[str, QtMultimedia.QMediaPlayer] = {}
        self._fallbacks = {
            "onetask.mp3": ["done.mp3"],
            "completedall.mp3": ["Completed.mp3", "done.mp3"],
            "deletetask.mp3": ["delete.mp3"],
            "createtask.mp3": ["done.mp3"],
            "sharetask.mp3": ["done.mp3"],
        }

    def play(self, filename: str) -> bool:
        """Play a sound from the project's sound directory."""
        if not self._sound_dir:
            return False

        candidates = [filename] + self._fallbacks.get(filename, [])
        for name in candidates:
            sound_path = self._sound_dir / name
            if not sound_path.exists():
                continue

            if self._play_native(sound_path):
                return True

            if self._play_qt(name, sound_path):
                return True

        return False

    def _create_player(self):
        try:
            player = QtMultimedia.QMediaPlayer()
        except Exception:
            return None

        if hasattr(player, "setAudioOutput") and hasattr(QtMultimedia, "QAudioOutput"):
            audio = QtMultimedia.QAudioOutput()
            audio.setVolume(1.0)
            player.setAudioOutput(audio)
            player._audio_output = audio  
        else:
            try:
                player.setVolume(100)
            except Exception:
                pass
        return player

    def _play_qt(self, cache_key: str, sound_path: Path) -> bool:
        url = QtCore.QUrl.fromLocalFile(str(sound_path))
        player = self._players.get(cache_key)
        if player is None:
            player = self._create_player()
            if player is None:
                return False
            self._players[cache_key] = player

        try:
            self._set_source(player, url)
            player.stop()
            player.play()
            return True
        except Exception:
            return False

    def _play_native(self, sound_path: Path) -> bool:
        """Use lightweight system player (helps on macOS)."""
        candidates = []
        if platform.system() == "Darwin":
            candidates.append("afplay")
        candidates.extend(["ffplay", "mpg123"])

        player = next((p for p in candidates if shutil.which(p)), None)
        if not player:
            return False

        try:
            if player == "ffplay":
                subprocess.Popen(
                    [player, "-nodisp", "-autoexit", str(sound_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen(
                    [player, str(sound_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return True
        except Exception:
            return False

    @staticmethod
    def _set_source(player, url: QtCore.QUrl):
        if hasattr(player, "setSource"):
            player.setSource(url)
        else:
            content = QtMultimedia.QMediaContent(url)
            player.setMedia(content)


sound_player = SoundPlayer()
