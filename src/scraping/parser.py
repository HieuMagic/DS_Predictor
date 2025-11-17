"""
HTML parsing functions for extracting car data from web pages.
"""
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


def parse_bonbanh_car_details(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Parse car details from Bonbanh.com page.
    
    Args:
        soup: BeautifulSoup object of the car detail page
        
    Returns:
        Dictionary containing car details
    """
    car_data = {}
    
    try:
        # Extract title
        title_div = soup.find('div', class_='title')
        if title_div and title_div.find('h1'):
            title = title_div.find('h1').text
            car_data['title'] = re.sub(r'\s+', ' ', title).strip()
        
        # Extract details
        detail_div = soup.find('div', class_='box_car_detail')
        if detail_div:
            mail_parents = detail_div.find_all('div', id='mail_parent')
            for mail_parent in mail_parents:
                label_elem = mail_parent.find('label')
                span_elem = mail_parent.find('span')
                
                if label_elem and span_elem:
                    label = re.sub(r'\s+', ' ', label_elem.text).strip()
                    value = re.sub(r'\s+', ' ', span_elem.text).strip()
                    
                    # Clean up label (remove colon if present)
                    label = label.rstrip(':')
                    car_data[label] = value
        
        car_data['source'] = 'bonbanh'
        
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
    Parse car details from Chotot.com page.
    
    Args:
        soup: BeautifulSoup object of the car detail page
        
    Returns:
        Dictionary containing car details
    """
    car_data = {}
    
    try:
        div_list = soup.find_all('div', class_='p1ja3eq0')
        
        for div in div_list:
            label_elem = div.find('span', class_='bwq0cbs')
            if label_elem:
                value_elem = label_elem.find_next_sibling('span')
                
                if value_elem:
                    label = label_elem.text.strip()
                    value = value_elem.text.strip()
                    car_data[label] = value
        
        car_data['source'] = 'chotot'
        
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
