""" 
HTML parsing functions for extracting car data from web pages.
"""
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


def split_price(title: str) -> int:
    """
    Extract price from Vietnamese title with Tỷ and Triệu.
    
    Args:
        title: Title string containing price
        
    Returns:
        Price in VND (integer)
    """
    match_ty = re.search(r'(\d+)\s*Tỷ', title, re.IGNORECASE)
    ty = int(match_ty.group(1)) if match_ty else 0
    
    match_trieu = re.search(r'(\d+)\s*Triệu', title, re.IGNORECASE)
    trieu = int(match_trieu.group(1)) if match_trieu else 0
    
    price = (ty * 1_000_000_000) + (trieu * 1_000_000)
    return price


def extract_model_from_title(title: str, brand: str) -> tuple:
    """
    Extract car model and year from title.
    
    Args:
        title: Title string
        brand: Brand code (e.g., 'mercedes_benz')
        
    Returns:
        Tuple of (model, year)
    """
    from .utils import BRAND_MAPPING
    
    # Remove price information
    price_pattern = r'\d+\s*Tỷ|\d+\s*Triệu'
    price_match = re.search(price_pattern, title)
    
    if price_match:
        title_without_price = title[:price_match.start()].strip()
    else:
        title_without_price = title
    
    # Remove brand name
    brand_display = BRAND_MAPPING.get(brand, brand).replace('_', ' ')
    title_lower = title_without_price.lower()
    brand_lower = brand_display.lower()
    
    if title_lower.startswith(brand_lower):
        remaining = title_without_price[len(brand_display):].strip()
    else:
        remaining = title_without_price
    
    # Remove "Xe {brand}" pattern
    xe_brand_pattern = rf'\bXe\s+{re.escape(brand_display)}\b'
    remaining = re.sub(xe_brand_pattern, '', remaining, flags=re.IGNORECASE).strip()
    
    # Extract year
    year_pattern = r'\b(19|20)\d{2}\b'
    year_match = re.search(year_pattern, remaining)
    
    if year_match:
        model = remaining[:year_match.start()].strip()
        year = year_match.group()
    else:
        words = remaining.split()
        model = ' '.join(words[:3]) if len(words) >= 3 else remaining
        year = None
    
    return model, year


def extract_engine_info(text: str) -> tuple:
    """
    Extract fuel type and engine capacity from engine description.
    
    Args:
        text: Engine description text
        
    Returns:
        Tuple of (fuel_type, engine_capacity)
    """
    if ":" in text:
        value_part = text.split(":", 1)[1].strip()
    else:
        value_part = text.strip()
    
    match = re.search(r'^(.*?)\s+(\d+(?:\.\d+)?)\s*L$', value_part, re.IGNORECASE)
    
    if match:
        fuel = match.group(1).strip()
        capacity = match.group(2).strip()
        return fuel, capacity
    else:
        return value_part, None


def parse_bonbanh_car_details(soup: BeautifulSoup, brand: str = None) -> Dict[str, str]:
    """
    Parse car details from Bonbanh.com page with structured output.
    
    Args:
        soup: BeautifulSoup object of the car detail page
        brand: Brand code for proper parsing
        
    Returns:
        Dictionary containing structured car details
    """
    from .utils import BRAND_MAPPING
    
    car_data = {
        'price': -1,
        'brand': -1,
        'model': -1,
        'year': -1,
        'odometer': -1,
        'transmission': -1,
        'fuel_type': -1,
        'engine_capacity': -1,
        'body_style': -1,
        'origin': -1,
        'seats': -1,
        'condition': -1,
        'num_owners': -1,
        'inspection_status': -1,
        'warranty_status': -1,
        'source': 'bonbanh'
    }
    
    try:
        # Extract title
        title_div = soup.find('div', class_='title')
        if title_div and title_div.find('h1'):
            title = title_div.find('h1').text
            title = re.sub(r'\s+', ' ', title).strip()
            
            # Extract price from title
            price = split_price(title)
            car_data['price'] = price if price else -1
            
            # Extract model and year from title if brand is provided
            if brand:
                car_data['brand'] = BRAND_MAPPING.get(brand, brand)
                model, year = extract_model_from_title(title, brand)
                car_data['model'] = model if model else -1
                car_data['year'] = year if year else -1
        
        # Extract details from the detail section
        detail_div = soup.find('div', class_='box_car_detail')
        if detail_div:
            mail_parents = detail_div.find_all('div', id='mail_parent')
            
            for mail_parent in mail_parents:
                label_elem = mail_parent.find('label')
                span_elem = mail_parent.find('span')
                
                if not label_elem or not span_elem:
                    continue
                
                label = re.sub(r'\s+', ' ', label_elem.text).strip().rstrip(':')
                value = re.sub(r'\s+', ' ', span_elem.text).strip()
                
                # Map labels to structured fields
                if label == 'Số Km đã đi':
                    car_data['odometer'] = re.sub(r'\D', '', value)
                elif label == 'Hộp số':
                    car_data['transmission'] = value
                elif label == 'Động cơ':
                    fuel_type, engine_capacity = extract_engine_info(value)
                    car_data['fuel_type'] = fuel_type if fuel_type else -1
                    car_data['engine_capacity'] = engine_capacity if engine_capacity else -1
                elif label == 'Kiểu dáng':
                    car_data['body_style'] = value
                elif label == 'Xuất xứ':
                    car_data['origin'] = value
                elif label == 'Số chỗ ngồi':
                    car_data['seats'] = value
                elif label == 'Tình trạng':
                    car_data['condition'] = value
                elif 'chủ' in label.lower():
                    car_data['num_owners'] = value
                elif 'kiểm định' in label.lower():
                    car_data['inspection_status'] = value
                elif 'bảo hành' in label.lower():
                    car_data['warranty_status'] = value
        
    except Exception as e:
        print(f"Error parsing Bonbanh car details: {e}")
    
    return car_data
def parse_bonbanh_listing(soup: BeautifulSoup) -> List[str]:
    """
    Parse car listing page from Bonbanh.com to extract car detail URLs.
    
    Args:
        soup: BeautifulSoup object of the listing page
        
    Returns:
        List of car detail URLs
    """
    car_links = []
    
    try:
        car_lis = soup.find_all('li', class_='car-item')
        
        for car_li in car_lis:
            a_link = car_li.find('a')
            if a_link and 'href' in a_link.attrs:
                link = a_link.attrs['href']
                full_link = 'https://bonbanh.com/' + link
                car_links.append(full_link)
                
    except Exception as e:
        print(f"Error parsing Bonbanh listing: {e}")
    
    return car_links


def parse_chotot_car_details(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Parse car details from Chotot.com page with structured output.
    
    Args:
        soup: BeautifulSoup object of the car detail page
        
    Returns:
        Dictionary containing structured car details
    """
    car_data = {
        'price': -1,
        'brand': -1,
        'model': -1,
        'year': -1,
        'odometer': -1,
        'transmission': -1,
        'fuel_type': -1,
        'engine_capacity': -1,
        'body_style': -1,
        'origin': -1,
        'seats': -1,
        'condition': -1,
        'num_owners': -1,
        'inspection_status': -1,
        'warranty_status': -1,
        'source': 'chotot'
    }
    
    try:
        # Extract title and price
        div_title = soup.find('div', class_='cpmughi')
        if div_title:
            price_elem = div_title.find('b', class_='p26z2wb')
            if price_elem:
                price_raw = price_elem.text.strip()
                price = re.sub(r'\D', '', price_raw)
                car_data['price'] = price if price else -1
        
        # Extract other details with field mapping
        div_list = soup.find_all('div', class_='p1ja3eq0')
        
        for div in div_list:
            label_elem = div.find('span', class_='bwq0cbs')
            if label_elem:
                value_elem = label_elem.find_next_sibling('span')
                
                if value_elem:
                    label = label_elem.text.strip()
                    value = value_elem.text.strip()
                    
                    # Map Vietnamese labels to English structured fields
                    if label == 'Số Km đã đi':
                        car_data['odometer'] = value
                    elif label == 'Hộp số':
                        car_data['transmission'] = value
                    elif label == 'Nhiên liệu':
                        car_data['fuel_type'] = value
                    elif label == 'Kiểu dáng':
                        car_data['body_style'] = value
                    elif label == 'Xuất xứ':
                        car_data['origin'] = value
                    elif label == 'Số chỗ':
                        car_data['seats'] = value
                    elif label == 'Tình trạng':
                        car_data['condition'] = value
                        if value == 'Đã sử dụng':
                            car_data['num_owners'] = '>1'
                    elif label == 'Còn hạn đăng kiểm':
                        car_data['inspection_status'] = value
                    elif label == 'Chính sách bảo hành':
                        car_data['warranty_status'] = value
                    elif label == 'Hãng':
                        car_data['brand'] = value
                    elif label == 'Năm sản xuất':
                        car_data['year'] = value
                    elif label == 'Dòng xe':
                        car_data['model'] = value
        
    except Exception as e:
        print(f"Error parsing Chotot car details: {e}")
    
    return car_data


def parse_chotot_listing(soup: BeautifulSoup) -> List[str]:
    """
    Parse car listing page from Chotot.com to extract car detail URLs.
    
    Args:
        soup: BeautifulSoup object of the listing page
        
    Returns:
        List of car detail URLs
    """
    car_links = []
    base_url = 'https://xe.chotot.com'
    
    try:
        a_list = soup.find_all('a', class_='c15fd2pn')
        
        for a in a_list:
            if 'href' in a.attrs:
                link = a.attrs['href']
                # Handle both relative and absolute URLs
                if not link.startswith('http'):
                    full_link = base_url + link
                else:
                    full_link = link
                car_links.append(full_link)
                
    except Exception as e:
        print(f"Error parsing Chotot listing: {e}")
    
    return car_links
