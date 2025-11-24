"""
SSL Certificate Auto-Installer
Automatically installs mitmproxy root certificate for HTTPS interception
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

class CertificateInstaller:
    """Installs mitmproxy SSL certificate"""
    
    def __init__(self):
        # mitmproxy stores cert in ~/.mitmproxy/
        if sys.platform == "win32":
            self.cert_dir = Path.home() / ".mitmproxy"
        else:
            self.cert_dir = Path.home() / ".mitmproxy"
        
        self.cert_file = self.cert_dir / "mitmproxy-ca-cert.pem"
    
    def install(self):
        """Install the certificate"""
        
        print("🔐 Installing mitmproxy SSL certificate...")
        
        # First, ensure mitmproxy has generated the cert
        if not self.cert_file.exists():
            print("⚠️ Certificate not found. Generating...")
            self._generate_cert()
        
        if sys.platform == "win32":
            return self._install_windows()
        elif sys.platform == "darwin":
            return self._install_mac()
        else:
            return self._install_linux()
    
    def _generate_cert(self):
        """Generate mitmproxy certificate"""
        try:
            # Run mitmdump briefly to generate cert
            proc = subprocess.Popen(
                ["mitmdump", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            proc.wait(timeout=5)
            
            # Check if cert was generated
            if self.cert_file.exists():
                print(f"✅ Certificate generated at: {self.cert_file}")
            else:
                print("❌ Failed to generate certificate")
                return False
        except Exception as e:
            print(f"❌ Error generating certificate: {e}")
            return False
        
        return True
    
    def _install_windows(self) -> bool:
        """Install certificate on Windows"""
        
        try:
            # Convert PEM to CER for Windows
            cer_file = self.cert_dir / "mitmproxy-ca-cert.cer"
            
            if not cer_file.exists():
                shutil.copy(self.cert_file, cer_file)
            
            # Use certutil to install
            cmd = ["certutil", "-addstore", "-f", "ROOT", str(cer_file)]
            
            print(f"Running: {' '.join(cmd)}")
            print("⚠️ This requires ADMINISTRATOR privileges!")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Certificate installed successfully!")
                print("💡 Browsers will now trust HTTPS interception")
                return True
            else:
                print(f"❌ Installation failed: {result.stderr}")
                print("\n📝 Manual installation:")
                print(f"1. Double-click: {cer_file}")
                print("2. Install Certificate → Local Machine")
                print("3. Place in 'Trusted Root Certification Authorities'")
                return False
                
        except FileNotFoundError:
            print("❌ certutil not found")
            print("\n📝 Manual installation required:")
            print(f"1. Open: {self.cert_file}")
            print("2. Install as Trusted Root CA")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def _install_mac(self) -> bool:
        """Install certificate on macOS"""
        
        try:
            cmd = [
                "sudo", "security", "add-trusted-cert",
                "-d", "-r", "trustRoot",
                "-k", "/Library/Keychains/System.keychain",
                str(self.cert_file)
            ]
            
            print(f"Running: {' '.join(cmd)}")
            print("⚠️ This requires sudo password!")
            
            result = subprocess.run(cmd)
            
            if result.returncode == 0:
                print("✅ Certificate installed successfully!")
                return True
            else:
                print("❌ Installation failed")
                print("\n📝 Manual installation:")
                print(f"1. Open Keychain Access")
                print(f"2. Import: {self.cert_file}")
                print("3. Trust for SSL")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def _install_linux(self) -> bool:
        """Install certificate on Linux"""
        
        try:
            # Copy to system cert directory
            cert_dest = Path("/usr/local/share/ca-certificates/mitmproxy.crt")
            
            print(f"Copying to: {cert_dest}")
            print("⚠️ This requires sudo!")
            
            subprocess.run([
                "sudo", "cp",
                str(self.cert_file),
                str(cert_dest)
            ])
            
            # Update CA certificates
            subprocess.run(["sudo", "update-ca-certificates"])
            
            print("✅ Certificate installed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("\n📝 Manual installation:")
            print(f"1. Copy {self.cert_file} to /usr/local/share/ca-certificates/")
            print("2. Run: sudo update-ca-certificates")
            return False
    
    def uninstall(self):
        """Uninstall the certificate"""
        
        print("🗑️ Uninstalling certificate...")
        
        if sys.platform == "win32":
            # Remove from Windows cert store
            cmd = ["certutil", "-delstore", "ROOT", "mitmproxy"]
            subprocess.run(cmd)
        
        print("✅ Certificate removed")


if __name__ == "__main__":
    installer = CertificateInstaller()
    
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        installer.uninstall()
    else:
        installer.install()
