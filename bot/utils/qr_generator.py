"""
QR Code generator for payment addresses
"""

import qrcode
import io
import base64
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

def generate_payment_qr(address: str, amount: Optional[float] = None, currency: str = "USDT") -> str:
    """Generate QR code for payment address"""
    
    # Create QR code data
    if amount:
        qr_data = f"{address}?amount={amount}&currency={currency}"
    else:
        qr_data = address
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Convert to base64 for easy transmission
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return img_base64

def generate_payment_qr_with_info(
    address: str, 
    amount: float, 
    currency: str = "USDT",
    network: str = "TRC20",
    invoice_id: str = None
) -> str:
    """Generate QR code with payment information overlay"""
    
    # Create basic QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    
    qr_data = address
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Create a larger canvas for additional info
    canvas_width = qr_img.width + 40
    canvas_height = qr_img.height + 120
    
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    
    # Paste QR code in center
    qr_x = (canvas_width - qr_img.width) // 2
    qr_y = 60
    canvas.paste(qr_img, (qr_x, qr_y))
    
    # Add text information
    draw = ImageDraw.Draw(canvas)
    
    try:
        # Try to use a better font
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        info_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        info_font = ImageFont.load_default()
    
    # Title
    title_text = f"Payment QR Code"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (canvas_width - title_width) // 2
    draw.text((title_x, 20), title_text, fill="black", font=title_font)
    
    # Payment info below QR code
    info_y = qr_y + qr_img.height + 20
    
    # Amount and currency
    amount_text = f"Amount: {amount} {currency}"
    amount_bbox = draw.textbbox((0, 0), amount_text, font=info_font)
    amount_width = amount_bbox[2] - amount_bbox[0]
    amount_x = (canvas_width - amount_width) // 2
    draw.text((amount_x, info_y), amount_text, fill="black", font=info_font)
    
    # Network
    network_text = f"Network: {network}"
    network_bbox = draw.textbbox((0, 0), network_text, font=info_font)
    network_width = network_bbox[2] - network_bbox[0]
    network_x = (canvas_width - network_width) // 2
    draw.text((network_x, info_y + 20), network_text, fill="black", font=info_font)
    
    # Invoice ID if provided
    if invoice_id:
        invoice_text = f"Invoice: {invoice_id[:8]}..."
        invoice_bbox = draw.textbbox((0, 0), invoice_text, font=info_font)
        invoice_width = invoice_bbox[2] - invoice_bbox[0]
        invoice_x = (canvas_width - invoice_width) // 2
        draw.text((invoice_x, info_y + 40), invoice_text, fill="gray", font=info_font)
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    canvas.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Convert to base64
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return img_base64

def save_qr_to_file(qr_base64: str, filename: str) -> bool:
    """Save base64 QR code to file"""
    
    try:
        # Decode base64
        img_data = base64.b64decode(qr_base64)
        
        # Save to file
        with open(filename, 'wb') as f:
            f.write(img_data)
        
        return True
    except Exception as e:
        print(f"Error saving QR code: {e}")
        return False

def create_crypto_payment_qr(
    address: str,
    amount: float,
    currency: str,
    network: str,
    memo: str = None
) -> str:
    """Create QR code for cryptocurrency payment"""
    
    # Build payment URI based on currency
    if currency.upper() == "BTC":
        uri = f"bitcoin:{address}?amount={amount}"
    elif currency.upper() in ["USDT", "USDC"]:
        uri = f"{currency.lower()}:{address}?amount={amount}&network={network}"
        if memo:
            uri += f"&memo={memo}"
    else:
        # Generic format
        uri = f"{currency.lower()}:{address}?amount={amount}"
        if memo:
            uri += f"&memo={memo}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    
    qr.add_data(uri)
    qr.make(fit=True)
    
    # Create image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return img_base64

def generate_invoice_qr(invoice_data: dict) -> str:
    """Generate QR code for invoice with all payment details"""
    
    address = invoice_data.get('address')
    amount = invoice_data.get('amount')
    currency = invoice_data.get('currency', 'USDT')
    network = invoice_data.get('network', 'TRC20')
    invoice_id = invoice_data.get('invoice_id')
    expires_at = invoice_data.get('expires_at')
    
    # Create comprehensive QR data
    qr_data = {
        'address': address,
        'amount': amount,
        'currency': currency,
        'network': network,
        'invoice_id': invoice_id
    }
    
    # Convert to string format
    qr_string = f"crypto:{address}?amount={amount}&currency={currency}&network={network}"
    if invoice_id:
        qr_string += f"&ref={invoice_id}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=2,  # Larger version for more data
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    
    qr.add_data(qr_string)
    qr.make(fit=True)
    
    # Create image with enhanced styling
    qr_img = qr.make_image(
        fill_color="#1a1a1a",  # Dark gray instead of black
        back_color="#ffffff"   # White background
    )
    
    # Add border and styling
    border_size = 20
    new_size = (qr_img.width + border_size * 2, qr_img.height + border_size * 2)
    
    styled_img = Image.new('RGB', new_size, '#f8f9fa')  # Light gray border
    styled_img.paste(qr_img, (border_size, border_size))
    
    # Convert to base64
    img_buffer = io.BytesIO()
    styled_img.save(img_buffer, format='PNG', quality=95)
    img_buffer.seek(0)
    
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return img_base64

