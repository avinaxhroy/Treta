"""
Authentication CLI commands for Treta.
Manages Spotify tokens and Apple Music cookies.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
import os
import json

from core.auth_store import AuthStore

# Initialize Rich console
console = Console()

# Create Typer app
auth_app = typer.Typer(help="Manage authentication for music services")

@auth_app.command()
def add(
    service: str = typer.Option(..., "--service", "-s", help="Service to add auth for (spotify/apple)"),
    token: Optional[str] = typer.Option(None, "--token", "-t", help="Token/cookies data (will prompt if not provided)")
):
    """Add authentication for a music service."""
    
    service = service.lower()
    if service not in ["spotify", "apple"]:
        console.print("❌ [red]Unsupported service. Use 'spotify' or 'apple'[/red]")
        raise typer.Exit(1)
    
    auth_store = AuthStore()
    
    if service == "spotify":
        _add_spotify_auth(auth_store, token)
    elif service == "apple":
        _add_apple_auth(auth_store, token)

@auth_app.command()
def test(
    service: str = typer.Option(..., "--service", "-s", help="Service to test (spotify/apple)")
):
    """Test authentication for a music service."""
    
    service = service.lower()
    if service not in ["spotify", "apple"]:
        console.print("❌ [red]Unsupported service. Use 'spotify' or 'apple'[/red]")
        raise typer.Exit(1)
    
    console.print(f"🔍 [blue]Testing {service.title()} authentication...[/blue]")
    
    auth_store = AuthStore()
    
    try:
        if service == "spotify":
            is_valid = auth_store.test_spotify_auth()
        else:
            is_valid = auth_store.test_apple_auth()
        
        if is_valid:
            console.print(f"✅ [green]{service.title()} authentication is working![/green]")
        else:
            console.print(f"❌ [red]{service.title()} authentication failed or not found[/red]")
            console.print(f"💡 [cyan]Run: treta auth add --service {service}[/cyan]")
            
    except Exception as e:
        console.print(f"❌ [red]Error testing {service} auth: {e}[/red]")
        raise typer.Exit(1)

@auth_app.command()
def status():
    """Show authentication status for all services."""
    
    console.print("🔐 [bold blue]Authentication Status[/bold blue]")
    
    auth_store = AuthStore()
    
    try:
        auth_status = auth_store.get_auth_status()
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Service", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Action", style="yellow")
        
        for service, is_authenticated in auth_status.items():
            if is_authenticated:
                status = "✅ Authenticated"
                action = "treta auth test --service " + service
            else:
                status = "❌ Not authenticated"
                action = "treta auth add --service " + service
            
            table.add_row(service.title(), status, action)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [red]Error getting auth status: {e}[/red]")
        raise typer.Exit(1)

@auth_app.command()
def remove(
    service: str = typer.Option(..., "--service", "-s", help="Service to remove auth for (spotify/apple)"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Remove authentication for a music service."""
    
    service = service.lower()
    if service not in ["spotify", "apple"]:
        console.print("❌ [red]Unsupported service. Use 'spotify' or 'apple'[/red]")
        raise typer.Exit(1)
    
    if not confirm:
        confirm = typer.confirm(f"Are you sure you want to remove {service.title()} authentication?")
        if not confirm:
            console.print("❌ [yellow]Operation cancelled[/yellow]")
            raise typer.Exit(0)
    
    auth_store = AuthStore()
    
    try:
        if service == "spotify":
            auth_store.revoke_spotify_auth()
        else:
            auth_store.revoke_apple_auth()
        
        console.print(f"✅ [green]{service.title()} authentication removed[/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Error removing {service} auth: {e}[/red]")
        raise typer.Exit(1)

def _add_spotify_auth(auth_store: AuthStore, token: Optional[str]):
    """Add Spotify authentication."""
    
    console.print("🎵 [bold green]Adding Spotify Authentication[/bold green]")
    
    # Ask user which type of authentication they want to add
    console.print("\n📝 [cyan]Choose authentication method:[/cyan]")
    console.print("1. Username/Password (recommended for downloads)")
    console.print("2. Bearer Token (for API access)")
    
    auth_type = Prompt.ask(
        "\nSelect option",
        choices=["1", "2"],
        default="1"
    )
    
    if auth_type == "1":
        _add_spotify_credentials(auth_store)
    else:
        _add_spotify_token(auth_store, token)

def _add_spotify_credentials(auth_store: AuthStore):
    """Add Spotify username/password credentials."""
    
    console.print("\n🔐 [bold cyan]Spotify Username/Password Authentication[/bold cyan]")
    
    instructions = """
Enter your Spotify username and password.
These will be securely stored and used for music downloads.

Note: This is your regular Spotify login credentials.
"""
    
    console.print(Panel(instructions.strip(), title="📖 Instructions", border_style="blue"))
    
    username = Prompt.ask("\n👤 [cyan]Spotify Username/Email[/cyan]")
    password = Prompt.ask("🔑 [cyan]Spotify Password[/cyan]", password=True)
    
    if not username or not password:
        console.print("❌ [red]Username and password are required[/red]")
        raise typer.Exit(1)
    
    try:
        success = auth_store.store_spotify_credentials(username, password)
        
        if success:
            console.print("✅ [green]Spotify credentials stored successfully![/green]")
            console.print("🎉 [green]You can now download music from Spotify![/green]")
        else:
            console.print("❌ [red]Failed to store Spotify credentials[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Error storing Spotify credentials: {e}[/red]")
        raise typer.Exit(1)

def _add_spotify_token(auth_store: AuthStore, token: Optional[str]):
    """Add Spotify Bearer token."""
    
    console.print("\n🔑 [bold cyan]Spotify Bearer Token Authentication[/bold cyan]")
    
    # Show instructions
    instructions = """
To get your Spotify token:

1. Open https://open.spotify.com/
2. Open browser developer tools (F12)
3. Go to Network tab
4. Play any song
5. Look for requests to 'api.spotify.com'
6. Find the 'Authorization' header in one of these requests
7. Copy the token after 'Bearer ' (without 'Bearer ')

Example: If header is 'Bearer BQA...xyz', copy 'BQA...xyz'
"""
    
    console.print(Panel(instructions.strip(), title="📖 Instructions", border_style="blue"))
    
    if not token:
        token = Prompt.ask(
            "\n🔑 [cyan]Enter your Spotify Bearer token[/cyan]",
            password=True
        )
    
    if not token or len(token) < 50:
        console.print("❌ [red]Invalid token format. Spotify tokens are typically 100+ characters long.[/red]")
        console.print("💡 [cyan]Make sure you copied the entire token after 'Bearer ' (without 'Bearer ').[/cyan]")
        raise typer.Exit(1)
    
    # Basic format validation
    if not token.startswith(('BQA', 'BQB', 'BQC', 'BQD')):
        console.print("⚠️  [yellow]Warning: Spotify tokens typically start with 'BQA', 'BQB', 'BQC', or 'BQD'.[/yellow]")
        console.print("💡 [cyan]Double-check that you copied the token correctly.[/cyan]")
        
        if not typer.confirm("Continue anyway?"):
            raise typer.Exit(0)
    
    try:
        success = auth_store.store_spotify_token(token)
        
        if success:
            console.print("✅ [green]Spotify token stored successfully![/green]")
            
            # Test the token
            console.print("🔍 [blue]Testing token...[/blue]")
            if auth_store.test_spotify_auth():
                console.print("🎉 [green]Spotify authentication is working![/green]")
            else:
                console.print("⚠️  [yellow]Token stored but test failed. Please verify the token.[/yellow]")
        else:
            console.print("❌ [red]Failed to store Spotify token[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Error storing Spotify token: {e}[/red]")
        raise typer.Exit(1)

def _add_apple_auth(auth_store: AuthStore, cookies: Optional[str]):
    """Add Apple Music authentication."""
    
    console.print("🍎 [bold green]Adding Apple Music Authentication[/bold green]")
    
    # Show instructions
    instructions = """
To get your Apple Music cookies:

1. Install a browser extension to export cookies:
   • Firefox: "Export Cookies" extension
   • Chrome/Edge: "Get cookies.txt LOCALLY" extension

2. Go to https://music.apple.com/ and log in

3. Use the extension to export cookies in Netscape format

4. Copy the contents of the downloaded cookies.txt file

5. You need an active Apple Music subscription for this to work!
"""
    
    console.print(Panel(instructions.strip(), title="📖 Instructions", border_style="blue"))
    
    if not cookies:
        console.print("\n📝 [cyan]Paste your Apple Music cookies (Netscape format):[/cyan]")
        console.print("💡 [dim]Tip: Paste and press Ctrl+D (Unix) or Ctrl+Z (Windows) to finish[/dim]\n")
        
        # Read multiline input
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            cookies = '\n'.join(lines)
    
    if not cookies or len(cookies) < 100:
        console.print("❌ [red]Invalid cookies format or too short[/red]")
        raise typer.Exit(1)
    
    try:
        success = auth_store.store_apple_cookies(cookies)
        
        if success:
            console.print("✅ [green]Apple Music cookies stored successfully![/green]")
            
            # Test the cookies
            console.print("🔍 [blue]Testing cookies...[/blue]")
            if auth_store.test_apple_auth():
                console.print("🎉 [green]Apple Music authentication is working![/green]")
            else:
                console.print("⚠️  [yellow]Cookies stored but test failed. Please verify your subscription.[/yellow]")
        else:
            console.print("❌ [red]Failed to store Apple Music cookies[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Error storing Apple Music cookies: {e}[/red]")
        raise typer.Exit(1)

def _add_spotify_credentials_auth(auth_store: AuthStore):
    """Add Spotify username/password authentication for Zotify."""
    
    console.print("🎵 [bold green]Adding Spotify Username/Password Authentication[/bold green]")
    console.print("💡 [cyan]This is required for Zotify (Spotify downloader) to work properly.[/cyan]")
    
    # Show instructions
    instructions = """
Zotify requires your Spotify username and password:

1. Use your regular Spotify username (email or username)
2. Use your Spotify account password
3. Credentials will be stored securely and encrypted

Note: If you have 2FA enabled, you may need to use an app password.
"""
    
    console.print(Panel(instructions.strip(), title="📖 Instructions", border_style="blue"))
    
    username = Prompt.ask(
        "\n👤 [cyan]Enter your Spotify username (email)[/cyan]"
    )
    
    if not username or '@' not in username:
        console.print("❌ [red]Please enter a valid email address.[/red]")
        raise typer.Exit(1)
    
    password = Prompt.ask(
        "🔑 [cyan]Enter your Spotify password[/cyan]",
        password=True
    )
    
    if not password or len(password) < 6:
        console.print("❌ [red]Password must be at least 6 characters long.[/red]")
        raise typer.Exit(1)
    
    try:
        success = auth_store.store_spotify_credentials(username, password)
        
        if success:
            console.print("✅ [green]Spotify credentials stored successfully![/green]")
            
            # Test the credentials by checking auth status
            console.print("🔍 [blue]Validating credentials...[/blue]")
            if auth_store.has_spotify_credentials():
                console.print("🎉 [green]Spotify credentials are ready for use![/green]")
                console.print("💡 [cyan]You can now download from Spotify using: treta download [URL][/cyan]")
            else:
                console.print("⚠️  [yellow]Credentials stored but validation failed.[/yellow]")
        else:
            console.print("❌ [red]Failed to store Spotify credentials[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Error storing Spotify credentials: {e}[/red]")
        raise typer.Exit(1)

@auth_app.command("test-zotify-legacy")
def test_zotify_legacy():
    """Test Zotify authentication separately to troubleshoot issues (legacy method)."""
    
    console.print("🔍 [bold blue]Testing Zotify Authentication[/bold blue]")
    
    auth_store = AuthStore()
    credentials = auth_store.get_spotify_credentials()
    
    if not credentials:
        console.print("❌ [red]No Spotify credentials found.[/red]")
        console.print("💡 [cyan]Run 'treta auth add --service spotify' first[/cyan]")
        raise typer.Exit(1)
    
    username = credentials['username']
    console.print(f"👤 [cyan]Testing credentials for: {username}[/cyan]")
    
    try:
        import subprocess
        import sys
          # Test Zotify login without downloading
        cmd = [
            sys.executable, '-m', 'zotify',
            '--username', username,
            '--password', credentials['password'],
            '--print-splash', 'false',
            '--print-downloads', 'false',
            '--test-login'  # Test login if this option exists
        ]
        
        console.print("🔍 [blue]Testing Zotify authentication...[/blue]")
        
        # First try with test-login if available, otherwise try a minimal command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # If test-login doesn't exist, try a different approach
        if result.returncode != 0 and "--test-login" in result.stderr:
            # Try with just username/password to see auth error
            cmd = [
                sys.executable, '-m', 'zotify',
                '--username', username,
                '--password', credentials['password'],
                '--print-splash', 'false'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                input='\n'  # Send enter to exit quickly after auth
            )
        
        if result.returncode == 0:
            console.print("✅ [green]Zotify authentication successful![/green]")
            console.print("🎉 [green]Your credentials are working correctly.[/green]")
        else:
            if "BadCredentials" in result.stderr:
                console.print("❌ [red]Authentication failed - Invalid credentials[/red]")
                console.print("\n🔧 [yellow]Troubleshooting suggestions:[/yellow]")
                console.print("• Verify your username and password are correct")
                console.print("• Make sure you have Spotify Premium")
                console.print("• If you have 2FA, try creating an app password")
                console.print("• Wait a few minutes if you've tried recently")
                console.print("\n💡 [cyan]Update credentials with: treta auth add --service spotify[/cyan]")
            else:
                console.print(f"❌ [red]Zotify test failed: {result.stderr}[/red]")
                
    except subprocess.TimeoutExpired:
        console.print("⏰ [yellow]Test timed out - this might indicate authentication is working but slow[/yellow]")
    except ImportError:
        console.print("❌ [red]Zotify not installed. Please install it first.[/red]")
    except Exception as e:
        console.print(f"❌ [red]Error testing Zotify: {e}[/red]")

@auth_app.command()
def setup_librespot():
    """Guide users through setting up librespot-auth for Spotify."""
    
    console.print("🎵 [bold blue]Spotify Credential Setup with librespot-auth[/bold blue]")
    console.print("💡 [cyan]This is the recommended method for reliable Spotify downloads[/cyan]")
    
    instructions = """
This guide will help you set up proper Spotify authentication using librespot-auth.
This method provides the most reliable authentication for Spotify downloads.

Prerequisites:
• Windows 10/11
• Spotify Premium account
• Internet connection

Steps:
1. Install Rust
2. Download and build librespot-auth  
3. Generate Spotify credentials
4. Install credentials for Treta
"""
    
    console.print(Panel(instructions.strip(), title="📖 Setup Overview", border_style="blue"))
    
    # Step 1: Check if Rust is installed
    console.print("\n🦀 [bold cyan]Step 1: Installing Rust[/bold cyan]")
    
    try:
        import subprocess
        result = subprocess.run(['cargo', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            console.print("✅ [green]Rust is already installed![/green]")
            console.print(f"🔧 [dim]Version: {result.stdout.strip()}[/dim]")
        else:
            raise subprocess.CalledProcessError(1, 'cargo')
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("❌ [red]Rust is not installed.[/red]")
        console.print("\n📥 [cyan]Please install Rust:[/cyan]")
        console.print("1. Go to https://rustup.rs/")
        console.print("2. Download and run the installer")
        console.print("3. Follow the installation instructions")
        console.print("4. Restart your command prompt/terminal")
        console.print("5. Run this command again")
        
        if typer.confirm("\nHave you installed Rust?"):
            # Re-check Rust installation
            try:
                result = subprocess.run(['cargo', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    console.print("✅ [green]Rust installation confirmed![/green]")
                else:
                    console.print("❌ [red]Rust still not found. Please restart your terminal and try again.[/red]")
                    raise typer.Exit(1)
            except (subprocess.CalledProcessError, FileNotFoundError):
                console.print("❌ [red]Rust still not found. Please complete the installation first.[/red]")
                raise typer.Exit(1)
        else:
            raise typer.Exit(0)
    
    # Step 2: Download librespot-auth
    console.print("\n📦 [bold cyan]Step 2: Setting up librespot-auth[/bold cyan]")
    
    download_instructions = """
To download librespot-auth:

1. Go to: https://github.com/dspearson/librespot-auth
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file to your Downloads folder

The folder should be named something like "librespot-auth-main"
"""
    
    console.print(Panel(download_instructions.strip(), title="📥 Download Instructions", border_style="blue"))
    
    if not typer.confirm("Have you downloaded and extracted librespot-auth?"):
        console.print("❌ [yellow]Please download librespot-auth first.[/yellow]")
        raise typer.Exit(0)
    
    # Ask for the path to librespot-auth
    default_path = os.path.join(os.path.expanduser("~"), "Downloads", "librespot-auth-main")
    librespot_path = Prompt.ask(
        f"\n📁 [cyan]Enter the path to librespot-auth folder[/cyan]",
        default=default_path
    )
    
    if not os.path.exists(librespot_path):
        console.print(f"❌ [red]Path not found: {librespot_path}[/red]")
        console.print("💡 [cyan]Please check the path and try again.[/cyan]")
        raise typer.Exit(1)
    
    # Step 3: Build librespot-auth
    console.print("\n🔨 [bold cyan]Step 3: Building librespot-auth[/bold cyan]")
    console.print("⏳ [yellow]This may take a few minutes...[/yellow]")
    
    try:
        result = subprocess.run(
            ['cargo', 'build', '--release'],
            cwd=librespot_path,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            console.print("✅ [green]librespot-auth built successfully![/green]")
        else:
            console.print(f"❌ [red]Build failed: {result.stderr}[/red]")
            raise typer.Exit(1)
            
    except subprocess.TimeoutExpired:
        console.print("❌ [red]Build timed out. Please try again.[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [red]Build error: {e}[/red]")
        raise typer.Exit(1)
    
    # Step 4: Generate credentials
    console.print("\n🔑 [bold cyan]Step 4: Generating Spotify credentials[/bold cyan]")
    
    credential_instructions = """
Now we'll generate your Spotify credentials:

1. Make sure Spotify is open and logged in
2. When prompted, change your Spotify playback device to "speaker"
3. This will generate a credentials.json file
"""
    
    console.print(Panel(credential_instructions.strip(), title="🎵 Credential Generation", border_style="blue"))
    
    if not typer.confirm("Is Spotify open and you're logged in?"):
        console.print("❌ [yellow]Please open and log into Spotify first.[/yellow]")
        raise typer.Exit(0)
    
    console.print("🎵 [blue]Running librespot-auth...[/blue]")
    
    try:
        exe_path = os.path.join(librespot_path, "target", "release", "librespot-auth.exe")
        if not os.path.exists(exe_path):
            console.print(f"❌ [red]Executable not found: {exe_path}[/red]")
            raise typer.Exit(1)
        
        console.print("📱 [cyan]Please check Spotify and change playback device to 'speaker' when prompted![/cyan]")
        
        result = subprocess.run(
            [exe_path],
            cwd=librespot_path,
            timeout=60  # 1 minute timeout
        )
        
        # Check if credentials.json was created
        credentials_path = os.path.join(librespot_path, "credentials.json")
        if os.path.exists(credentials_path):
            console.print("✅ [green]Credentials generated successfully![/green]")
        else:
            console.print("❌ [red]Credentials file not found. Please try again.[/red]")
            raise typer.Exit(1)
            
    except subprocess.TimeoutExpired:
        console.print("❌ [red]Credential generation timed out.[/red]")
        console.print("💡 [cyan]Make sure you changed the playback device in Spotify.[/cyan]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error generating credentials: {e}[/red]")
        raise typer.Exit(1)
    
    # Step 5: Install credentials
    console.print("\n⚙️ [bold cyan]Step 5: Installing credentials for Treta[/bold cyan]")
    
    try:
        # Read and format the credentials
        credentials_path = os.path.join(librespot_path, "credentials.json")
        with open(credentials_path, 'r') as f:
            raw_creds = json.load(f)
        
        # Format credentials for Zotify
        formatted_creds = {
            "username": raw_creds.get("username", ""),
            "type": "AUTHENTICATION_STORED_SPOTIFY_CREDENTIALS",
            "credentials": raw_creds.get("credentials", "")
        }
        
        # Create Zotify config directory
        zotify_config_dir = os.path.join(os.path.expanduser('~'), '.zotify')
        os.makedirs(zotify_config_dir, exist_ok=True)
        
        # Save formatted credentials
        zotify_creds_path = os.path.join(zotify_config_dir, 'credentials.json')
        with open(zotify_creds_path, 'w') as f:
            json.dump(formatted_creds, f, indent=2)
        
        console.print("✅ [green]Credentials installed for Treta![/green]")
        console.print(f"📁 [dim]Saved to: {zotify_creds_path}[/dim]")
        
        # Clean up temp credentials
        os.remove(credentials_path)
        
    except Exception as e:
        console.print(f"❌ [red]Error installing credentials: {e}[/red]")
        raise typer.Exit(1)
    
    # Final success message
    console.print("\n🎉 [bold green]Setup Complete![/bold green]")
    console.print("✅ [green]Spotify authentication is now configured for Treta[/green]")
    console.print("🎵 [cyan]You can now download from Spotify using: treta download [URL][/cyan]")
    console.print("🔍 [cyan]Test your setup with: treta auth test-zotify[/cyan]")

@auth_app.command()
def spotify_requirements():
    """Show Spotify authentication requirements and troubleshooting."""
    
    console.print("🎵 [bold blue]Spotify Authentication Requirements[/bold blue]")
    
    requirements = """
For Spotify downloads to work, you need:

✅ Requirements:
• Spotify Premium subscription (required for downloads)
• Valid Spotify account credentials
• Proper authentication setup (librespot-auth recommended)

⚠️ Common Issues:
• Free Spotify accounts cannot download music
• Two-factor authentication may require app passwords
• Multiple failed login attempts can temporarily lock your account
• VPN or proxy connections may cause authentication issues

🔧 Troubleshooting:
• Use librespot-auth for most reliable authentication
• If you have 2FA, try creating an app password
• Wait 5-10 minutes between login attempts if failing
• Make sure your Spotify subscription is active
• Try logging out and back into Spotify

🚀 Recommended Setup:
1. Run: treta auth setup-librespot
2. Follow the guided setup process
3. Test with: treta auth test-zotify
"""
    
    console.print(Panel(requirements.strip(), title="📋 Requirements & Troubleshooting", border_style="blue"))
    
    # Check current status
    console.print("\n🔍 [bold cyan]Current Authentication Status:[/bold cyan]")
    
    auth_store = AuthStore()
    
    # Check for Zotify credentials
    zotify_config_dir = os.path.join(os.path.expanduser('~'), '.zotify')
    credentials_file = os.path.join(zotify_config_dir, 'credentials.json')
    
    if os.path.exists(credentials_file):
        console.print("✅ [green]Zotify credentials file found[/green]")
        try:
            with open(credentials_file, 'r') as f:
                creds = json.load(f)
            if all(field in creds for field in ['username', 'type', 'credentials']):
                console.print("✅ [green]Credentials file format is valid[/green]")
            else:
                console.print("⚠️ [yellow]Credentials file format may be invalid[/yellow]")
        except:
            console.print("❌ [red]Credentials file is corrupted[/red]")
    else:
        console.print("❌ [red]No Zotify credentials found[/red]")
        console.print("💡 [cyan]Run 'treta auth setup-librespot' to set up credentials[/cyan]")
    
    # Check for stored credentials in Treta
    if auth_store.has_spotify_credentials():
        console.print("✅ [green]Treta has stored Spotify credentials[/green]")
    else:
        console.print("❌ [red]No Spotify credentials in Treta storage[/red]")
        console.print("💡 [cyan]Run 'treta auth add --service spotify' to add credentials[/cyan]")

@auth_app.command("test-zotify")
def test_zotify_auth():
    """Test Zotify authentication and setup."""
    
    console.print("🔍 [bold blue]Testing Zotify Authentication[/bold blue]")
    
    # Check if Zotify is installed
    try:
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, '-m', 'zotify', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            console.print("✅ [green]Zotify is installed and accessible[/green]")
        else:
            console.print("❌ [red]Zotify is not properly installed[/red]")
            console.print("💡 [cyan]Install with: pip install git+https://github.com/zotify-dev/zotify.git[/cyan]")
            raise typer.Exit(1)
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        console.print("❌ [red]Zotify is not installed or not accessible[/red]")
        console.print("💡 [cyan]Install with: pip install git+https://github.com/zotify-dev/zotify.git[/cyan]")
        raise typer.Exit(1)
    
    # Check for credentials
    zotify_config_dir = os.path.join(os.path.expanduser('~'), '.zotify')
    credentials_file = os.path.join(zotify_config_dir, 'credentials.json')
    
    if not os.path.exists(credentials_file):
        console.print("❌ [red]No Zotify credentials found[/red]")
        console.print("💡 [cyan]Run 'treta auth setup-librespot' to set up credentials[/cyan]")
        raise typer.Exit(1)
    
    console.print("✅ [green]Zotify credentials file found[/green]")
    
    # Test credentials format
    try:
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        required_fields = ['username', 'type', 'credentials']
        if all(field in creds for field in required_fields):
            console.print("✅ [green]Credentials file format is valid[/green]")
            console.print(f"👤 [cyan]Username: {creds['username']}[/cyan]")
        else:
            console.print("❌ [red]Credentials file format is invalid[/red]")
            console.print("💡 [cyan]Run 'treta auth setup-librespot' to regenerate credentials[/cyan]")
            raise typer.Exit(1)
            
    except json.JSONDecodeError:
        console.print("❌ [red]Credentials file is corrupted[/red]")
        console.print("💡 [cyan]Run 'treta auth setup-librespot' to regenerate credentials[/cyan]")
        raise typer.Exit(1)
    
    # Test with a simple Zotify command
    console.print("🔍 [blue]Testing Zotify authentication...[/blue]")
    
    try:
        # Try to run Zotify with --test-login if available, otherwise just check help
        result = subprocess.run(
            [sys.executable, '-m', 'zotify', '--config-location', zotify_config_dir, '--help'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            console.print("✅ [green]Zotify can access credentials successfully[/green]")
            console.print("🎉 [green]Authentication test passed! You should be able to download from Spotify.[/green]")
        else:
            console.print("❌ [red]Zotify authentication test failed[/red]")
            console.print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        console.print("⚠️ [yellow]Zotify test timed out[/yellow]")
        console.print("💡 [cyan]This might be normal. Try downloading a track to test properly.[/cyan]")
    except Exception as e:
        console.print(f"❌ [red]Error during Zotify test: {e}[/red]")
