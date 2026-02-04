#!/usr/bin/env python3
"""
Script to fork baby-monitor with audio support to your repository
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Output: {e.output}")
        return False

def main():
    print("🚀 Fork del Baby Monitor con Audio a tu repositorio")
    print("=" * 50)

    # Get user's GitHub username
    username = input("Ingresa tu nombre de usuario de GitHub: ").strip()
    if not username:
        print("❌ Nombre de usuario requerido")
        return

    repo_name = input("Nombre del nuevo repositorio (default: baby-monitor-audio): ").strip()
    if not repo_name:
        repo_name = "baby-monitor-audio"

    new_repo_url = f"https://github.com/{username}/{repo_name}.git"

    print(f"\n📋 Plan:")
    print(f"  - Repositorio original: https://github.com/Recentlystarted/baby-monitor.git")
    print(f"  - Nuevo repositorio: {new_repo_url}")
    print(f"  - Archivos incluidos: Baby Monitor con audio + multi-cámara")

    if input("\n¿Continuar? (y/N): ").lower() != 'y':
        print("❌ Cancelado")
        return

    # Check git status
    if not run_command("git status --porcelain", "Verificando estado de git"):
        return

    # Add all changes
    if not run_command("git add .", "Agregando cambios"):
        return

    # Commit changes
    commit_msg = "Add audio streaming and multi-camera support\\n\\n- Audio capture with sounddevice\\n- Multi-camera detection and selection\\n- Web audio streaming\\n- Graceful audio fallback"
    if not run_command(f'git commit -m "{commit_msg}"', "Haciendo commit"):
        return

    # Create new remote
    if not run_command(f"git remote add fork {new_repo_url}", "Agregando remote del fork"):
        return

    # Push to new repository
    if not run_command("git push -u fork main", "Subiendo al nuevo repositorio"):
        return

    print("\n🎉 ¡Fork completado exitosamente!")
    print(f"📁 Tu repositorio: https://github.com/{username}/{repo_name}")
    print("🔗 Comparte este enlace con otros usuarios")
if __name__ == "__main__":
    main()