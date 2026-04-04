export interface Product {
  id: string;
  name: string;
  category: 'laptop' | 'mobile' | 'pc';
  price: number;
  brand: string;
  specs: string;
  stock: number;
  image: string;
}

export const mockProducts: Product[] = [
  {
    id: 'L001',
    name: 'ASUS ROG Strix G18 G815LM S9088W',
    category: 'laptop',
    price: 65990000,
    brand: 'ASUS',
    specs: 'Intel Core i9, 32GB RAM, 1TB SSD',
    stock: 10000,
    image: '/assets/laptop-asus-rog-strix-g18-g815lm-s9088w.png'
  },
  {
    id: 'L002',
    name: 'ASUS ROG Strix G18 G815LR S9211W',
    category: 'laptop',
    price: 63990000,
    brand: 'ASUS',
    specs: 'Intel Core i9, 32GB RAM, 1TB SSD',
    stock: 10000,
    image: '/assets/laptop-asus-rog-strix-g18-g815lr-s9211w.png'
  },
  {
    id: 'L003',
    name: 'ASUS ROG Strix SCAR 18 G835LW',
    category: 'laptop',
    price: 72990000,
    brand: 'ASUS',
    specs: 'Intel Core Ultra 9, 32GB RAM, 1TB SSD',
    stock: 10000,
    image: '/assets/laptop-asus-rog-strix-scar-18-g835lw.png'
  },
  {
    id: 'L004',
    name: 'ASUS ROG Zephyrus G14 GA403WM',
    category: 'laptop',
    price: 45990000,
    brand: 'ASUS',
    specs: 'Ryzen 9, 16GB RAM, 1TB SSD',
    stock: 10000,
    image: '/assets/laptop-asus-rog-zephyrus-g14-ga403wm.png'
  },
  {
    id: 'L005',
    name: 'ASUS ROG Strix G16 G615JPR S5107W',
    category: 'laptop',
    price: 48990000,
    brand: 'ASUS',
    specs: 'Intel Core i9, 16GB RAM, 1TB SSD',
    stock: 10000,
    image: '/assets/laptop-asus-rog-strix-g16-g615jpr-s5107w.png'
  },
  {
    id: 'L006',
    name: 'ROG Strix SCAR 18 (2025) G835LW-SA172W',
    category: 'laptop',
    price: 81990000,
    brand: 'ASUS',
    specs: 'Intel Core Ultra 9 275HX, RTX 5080, 64GB RAM, 4TB SSD, 18" 2.5K 240Hz Mini LED',
    stock: 10000,
    image: '/assets/laptop-asus-rog-strix-scar-18-g835lw-sa172w.png'
  },
  {
    id: 'M001',
    name: 'iPhone 17 Pro Max 256GB',
    category: 'mobile',
    price: 38990000,
    brand: 'Apple',
    specs: 'A19 Pro, 256GB, 6.9" OLED',
    stock: 10000,
    image: '/assets/mobile-iphone-17-pro-max-256gb.png'
  },
  {
    id: 'M002',
    name: 'Samsung Galaxy S25 Ultra 12GB 256GB',
    category: 'mobile',
    price: 33990000,
    brand: 'Samsung',
    specs: '12GB RAM, 256GB, 6.8" AMOLED',
    stock: 10000,
    image: '/assets/mobile-samsung-galaxy-s25-ultra-12gb-256gb.png'
  },
  {
    id: 'M003',
    name: 'Samsung Galaxy Z Fold7 12GB 256GB',
    category: 'mobile',
    price: 42990000,
    brand: 'Samsung',
    specs: '12GB RAM, 256GB, Foldable AMOLED',
    stock: 10000,
    image: '/assets/mobile-samsung-galaxy-z-fold7-12gb-256gb.png'
  },
  {
    id: 'M004',
    name: 'Xiaomi 14T Pro 12GB 512GB',
    category: 'mobile',
    price: 19990000,
    brand: 'Xiaomi',
    specs: '12GB RAM, 512GB, 6.67" AMOLED',
    stock: 10000,
    image: '/assets/mobile-xiaomi-14t-pro-12gb-512gb.png'
  }
];

export interface CartItem extends Product {
  quantity: number;
}
