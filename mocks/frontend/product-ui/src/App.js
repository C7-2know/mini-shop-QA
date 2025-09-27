import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  // Authentication state
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [loginError, setLoginError] = useState('');

  // Product state
  const [products, setProducts] = useState([]);
  const [filters, setFilters] = useState({ category: '', minPrice: '', maxPrice: '' });
  const [loading, setLoading] = useState(false);

  // Cart state
  const [cart, setCart] = useState([]);
  const [cartId, setCartId] = useState(null);
  const [cartTotal, setCartTotal] = useState(0);

  // Checkout state
  const [checkoutForm, setCheckoutForm] = useState({
    address: { street: '', city: '', state: '', zip: '', country: '' },
    card: { number: '', expiry: '', cvv: '', name: '' }
  });
  const [checkoutErrors, setCheckoutErrors] = useState({});

  // Order state
  const [currentOrder, setCurrentOrder] = useState(null);
  const [currentView, setCurrentView] = useState('login'); // login, products, cart, checkout, confirmation

  // Load products on component mount
  useEffect(() => {
    if (isLoggedIn) {
      loadProducts();
    }
  }, [isLoggedIn]);

  // Authentication functions
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/login`, loginForm);
      setIsLoggedIn(true);
      setUser({ username: loginForm.username });
      setCurrentView('products');
      setLoginForm({ username: '', password: '' });
    } catch (error) {
      setLoginError('Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUser(null);
    setCurrentView('login');
    setCart([]);
    setCartId(null);
    setCurrentOrder(null);
  };

  // Product functions
  const loadProducts = async () => {
    setLoading(true);
    console.log("filters:", filters);
    const apiFilters = { ...filters };
    try {
      if (apiFilters.minPrice === '') {
        apiFilters.minPrice = 0;
      }
      if (apiFilters.maxPrice === '') {
        apiFilters.maxPrice = 3000000000000;
      }
      const response = await axios.get(`${API_BASE_URL}/products`, {
        params: apiFilters
      });
      console.log('Products loaded:', response.data);
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);  
    }
  };

  const handleFilterChange = (field, value) => {
    const numericValue = value === '' ? '' : Number(value);
    setFilters(prev => ({ ...prev, [field]: numericValue }));
  };

  const applyFilters = () => {
    loadProducts();
  };

  // Cart functions
  const addToCart = async (product, quantity = 1) => {
    try {
      const existingItem = cart.find(item => item.productId === product.id);
      let newCart;
      
      if (existingItem) {
        newCart = cart.map(item =>
          item.productId === product.id
            ? { ...item, qty: item.qty + quantity }
            : item
        );
      } else {
        newCart = [...cart, { productId: product.id, qty: quantity, product }];
      }

      const response = await axios.post(`${API_BASE_URL}/cart`, {
        items: newCart.map(item => ({ productId: item.productId, qty: item.qty }))
      });

      setCart(newCart);
      setCartId(response.data.cartId);
      setCartTotal(response.data.totalBeforeTax);
    } catch (error) {
      console.error('Failed to add to cart:', error);
    }
  };

  const removeFromCart = async (productId) => {
    const newCart = cart.filter(item => item.productId !== productId);
    setCart(newCart);
    
    if (newCart.length > 0) {
      try {
        const response = await axios.post(`${API_BASE_URL}/cart`, {
          items: newCart.map(item => ({ productId: item.productId, qty: item.qty }))
        });
        setCartTotal(response.data.totalBeforeTax);
      } catch (error) {
        console.error('Failed to update cart:', error);
      }
    } else {
      setCartTotal(0);
    }
  };

  const updateCartQuantity = async (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }

    const newCart = cart.map(item =>
      item.productId === productId ? { ...item, qty: newQuantity } : item
    );
    setCart(newCart);

    try {
      const response = await axios.post(`${API_BASE_URL}/cart`, {
        items: newCart.map(item => ({ productId: item.productId, qty: item.qty }))
      });
      setCartTotal(response.data.totalBeforeTax);
    } catch (error) {
      console.error('Failed to update cart:', error);
    }
  };

  // Checkout functions
  const validateCheckoutForm = () => {
    const errors = {};
    
    // Address validation
    if (!checkoutForm.address.street) errors.street = 'Street address is required';
    if (!checkoutForm.address.city) errors.city = 'City is required';
    if (!checkoutForm.address.state) errors.state = 'State is required';
    if (!checkoutForm.address.zip) errors.zip = 'ZIP code is required';
    if (!checkoutForm.address.country) errors.country = 'Country is required';

    // Card validation
    if (!checkoutForm.card.number) errors.cardNumber = 'Card number is required';
    if (!checkoutForm.card.expiry) errors.cardExpiry = 'Expiry date is required';
    if (!checkoutForm.card.cvv) errors.cardCvv = 'CVV is required';
    if (!checkoutForm.card.name) errors.cardName = 'Cardholder name is required';

    setCheckoutErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCheckout = async (e) => {
    e.preventDefault();
    
    if (!validateCheckoutForm()) return;

    setLoading(true);
    try {
      console.log(cartId, checkoutForm.address, checkoutForm.card);

      const response = await axios.post(`${API_BASE_URL}/checkout`, {
        cartId,
        address: checkoutForm.address,
        card: checkoutForm.card
      });

      setCurrentOrder(response.data);
      setCurrentView('confirmation');
      setCart([]);
      setCartId(null);
    } catch (error) {
      console.error('Checkout failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getOrderDetails = async (orderId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/order/${orderId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get order details:', error);
    }
  };

  // Render functions
  const renderLogin = () => (
    <div className="login-container">
      <div className="login-card">
        <h1 className="logo">MiniShop</h1>
        <p className="subtitle">Welcome back! Please sign in to continue.</p>
        
        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
          <input
              type="text"
            placeholder="Username"
              value={loginForm.username}
              onChange={(e) => setLoginForm(prev => ({ ...prev, username: e.target.value }))}
              className="form-input"
              required
            />
          </div>
          
          <div className="form-group">
          <input
            type="password"
            placeholder="Password"
              value={loginForm.password}
              onChange={(e) => setLoginForm(prev => ({ ...prev, password: e.target.value }))}
              className="form-input"
              required
            />
          </div>
          
          {loginError && <div className="error-message">{loginError}</div>}
          
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );

  const renderProducts = () => (
    <div className="products-container">
      <header className="header">
        <h1>MiniShop</h1>
        <div className="header-actions">
          <button onClick={() => setCurrentView('cart')} className="btn btn-outline">
            Cart ({cart.length})
          </button>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </header>

      <div className="filters-section">
        <h2>Filter Products</h2>
        <div className="filters">
          <input
            type="text"
            placeholder="Category"
            value={filters.category}
            onChange={(e) => handleFilterChange('category', e.target.value)}
            className="form-input"
          />
          <input
            type="number"
            placeholder="Min Price"
            value={filters.minPrice}
            onChange={(e) => handleFilterChange('minPrice', e.target.value)}
            className="form-input"
          />
          <input
            type="number"
            placeholder="Max Price"
            value={filters.maxPrice}
            onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
            className="form-input"
          />
          <button onClick={applyFilters} className="btn btn-primary">
            Apply Filters
          </button>
        </div>
      </div>

      <div className="products-grid">
        {loading ? (
          <div className="loading">Loading products...</div>
        ) : products.length === 0 ? (
          <div className="no-products">No products found</div>
        ) : (
          products.map(product => (
            <div key={product.id} className="product-card">
              <div className="product-info">
                <h3>{product.name}</h3>
                <p className="product-category">{product.category}</p>
                <p className="product-price">${product.price}</p>
              </div>
              <button
                onClick={() => addToCart(product)}
                className="btn btn-primary btn-small"
              >
                Add to Cart
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );

  const renderCart = () => (
    <div className="cart-container">
      <header className="header">
        <h1>Shopping Cart</h1>
        <div className="header-actions">
          <button onClick={() => setCurrentView('products')} className="btn btn-outline">
            Continue Shopping
          </button>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </header>

      {cart.length === 0 ? (
        <div className="empty-cart">
          <h2>Your cart is empty</h2>
          <p>Add some products to get started!</p>
          <button onClick={() => setCurrentView('products')} className="btn btn-primary">
            Browse Products
          </button>
        </div>
      ) : (
        <div className="cart-content">
          <div className="cart-items">
            {cart.map(item => (
              <div key={item.productId} className="cart-item">
                <div className="item-info">
                  <h3>{item.product.name}</h3>
                  <p className="item-category">{item.product.category}</p>
                  <p className="item-price">${item.product.price} each</p>
                </div>
                <div className="item-controls">
                  <div className="quantity-controls">
                    <button
                      onClick={() => updateCartQuantity(item.productId, item.qty - 1)}
                      className="btn btn-small"
                    >
                      -
                    </button>
                    <span className="quantity">{item.qty}</span>
                    <button
                      onClick={() => updateCartQuantity(item.productId, item.qty + 1)}
                      className="btn btn-small"
                    >
                      +
                    </button>
                  </div>
                  <button
                    onClick={() => removeFromCart(item.productId)}
                    className="btn btn-danger btn-small"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="cart-summary">
            <div className="summary-row">
              <span>Subtotal:</span>
              <span>${cartTotal.toFixed(2)}</span>
            </div>
            <div className="summary-total">
              <span>Total:</span>
              <span>${cartTotal.toFixed(2)}</span>
            </div>
            <button
              onClick={() => setCurrentView('checkout')}
              className="btn btn-primary btn-large"
            >
              Proceed to Checkout
            </button>
          </div>
        </div>
      )}
    </div>
  );

  const renderCheckout = () => (
    <div className="checkout-container">
      <header className="header">
        <h1>Checkout</h1>
        <div className="header-actions">
          <button onClick={() => setCurrentView('cart')} className="btn btn-outline">
            Back to Cart
          </button>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </header>

      <div className="checkout-content">
        <form onSubmit={handleCheckout} className="checkout-form">
          <div className="form-section">
            <h2>Shipping Address</h2>
            <div className="form-row">
              <div className="form-group">
                <input
                  type="text"
                  placeholder="Street Address"
                  value={checkoutForm.address.street}
                  onChange={(e) => setCheckoutForm(prev => ({
                    ...prev,
                    address: { ...prev.address, street: e.target.value }
                  }))}
                  className={`form-input ${checkoutErrors.street ? 'error' : ''}`}
                />
                {checkoutErrors.street && <span className="error-text">{checkoutErrors.street}</span>}
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <input
                  type="text"
                  placeholder="City"
                  value={checkoutForm.address.city}
                  onChange={(e) => setCheckoutForm(prev => ({
                    ...prev,
                    address: { ...prev.address, city: e.target.value }
                  }))}
                  className={`form-input ${checkoutErrors.city ? 'error' : ''}`}
                />
                {checkoutErrors.city && <span className="error-text">{checkoutErrors.city}</span>}
              </div>
              <div className="form-group">
                <input
                  type="text"
                  placeholder="State"
                  value={checkoutForm.address.state}
                  onChange={(e) => setCheckoutForm(prev => ({
                    ...prev,
                    address: { ...prev.address, state: e.target.value }
                  }))}
                  className={`form-input ${checkoutErrors.state ? 'error' : ''}`}
                />
                {checkoutErrors.state && <span className="error-text">{checkoutErrors.state}</span>}
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <input
                  type="text"
                  placeholder="ZIP Code"
                  value={checkoutForm.address.zip}
                  onChange={(e) => setCheckoutForm(prev => ({
                    ...prev,
                    address: { ...prev.address, zip: e.target.value }
                  }))}
                  className={`form-input ${checkoutErrors.zip ? 'error' : ''}`}
                />
                {checkoutErrors.zip && <span className="error-text">{checkoutErrors.zip}</span>}
              </div>
              <div className="form-group">
                <input
                  type="text"
                  placeholder="Country"
                  value={checkoutForm.address.country}
                  onChange={(e) => setCheckoutForm(prev => ({
                    ...prev,
                    address: { ...prev.address, country: e.target.value }
                  }))}
                  className={`form-input ${checkoutErrors.country ? 'error' : ''}`}
                />
                {checkoutErrors.country && <span className="error-text">{checkoutErrors.country}</span>}
              </div>
            </div>
          </div>

          <div className="form-section">
            <h2>Payment Information</h2>
            <div className="form-group">
              <input
                type="text"
                placeholder="Cardholder Name"
                value={checkoutForm.card.name}
                onChange={(e) => setCheckoutForm(prev => ({
                  ...prev,
                  card: { ...prev.card, name: e.target.value }
                }))}
                className={`form-input ${checkoutErrors.cardName ? 'error' : ''}`}
              />
              {checkoutErrors.cardName && <span className="error-text">{checkoutErrors.cardName}</span>}
            </div>
            
            <div className="form-group">
              <input
                type="text"
                placeholder="Card Number"
                value={checkoutForm.card.number}
                onChange={(e) => setCheckoutForm(prev => ({
                  ...prev,
                  card: { ...prev.card, number: e.target.value }
                }))}
                className={`form-input ${checkoutErrors.cardNumber ? 'error' : ''}`}
              />
              {checkoutErrors.cardNumber && <span className="error-text">{checkoutErrors.cardNumber}</span>}
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <input
                  type="text"
                  placeholder="MM/YY"
                  value={checkoutForm.card.expiry}
                  onChange={(e) => setCheckoutForm(prev => ({
                    ...prev,
                    card: { ...prev.card, expiry: e.target.value }
                  }))}
                  className={`form-input ${checkoutErrors.cardExpiry ? 'error' : ''}`}
                />
                {checkoutErrors.cardExpiry && <span className="error-text">{checkoutErrors.cardExpiry}</span>}
              </div>
              <div className="form-group">
                <input
                  type="text"
                  placeholder="CVV"
                  value={checkoutForm.card.cvv}
                  onChange={(e) => setCheckoutForm(prev => ({
                    ...prev,
                    card: { ...prev.card, cvv: e.target.value }
                  }))}
                  className={`form-input ${checkoutErrors.cardCvv ? 'error' : ''}`}
                />
                {checkoutErrors.cardCvv && <span className="error-text">{checkoutErrors.cardCvv}</span>}
              </div>
            </div>
          </div>

          <div className="checkout-summary">
            <h3>Order Summary</h3>
            <div className="summary-row">
              <span>Subtotal:</span>
              <span>${cartTotal.toFixed(2)}</span>
            </div>
            <div className="summary-total">
              <span>Total:</span>
              <span>${cartTotal.toFixed(2)}</span>
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-large" disabled={loading}>
            {loading ? 'Processing...' : 'Complete Order'}
          </button>
        </form>
      </div>
    </div>
  );

  const renderConfirmation = () => (
    <div className="confirmation-container">
      <div className="confirmation-card">
        <div className="success-icon">✓</div>
        <h1>Order Confirmed!</h1>
        <p className="order-id">Order ID: {currentOrder?.orderId}</p>
        
        <div className="order-summary">
          <h3>Order Details</h3>
          <div className="summary-row">
            <span>Subtotal:</span>
            <span>${currentOrder?.totalWithTax ? (currentOrder.totalWithTax - (currentOrder.taxApplied || 0)).toFixed(2) : '0.00'}</span>
          </div>
          <div className="summary-row">
            <span>Tax:</span>
            <span>${currentOrder?.taxApplied?.toFixed(2) || '0.00'}</span>
          </div>
          <div className="summary-total">
            <span>Total:</span>
            <span>${currentOrder?.totalWithTax?.toFixed(2) || '0.00'}</span>
          </div>
        </div>

        <div className="confirmation-actions">
          <button onClick={() => setCurrentView('products')} className="btn btn-primary">
            Continue Shopping
          </button>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </div>
    </div>
  );

  // Main render
  if (!isLoggedIn) {
    return renderLogin();
  }

  switch (currentView) {
    case 'products':
      return renderProducts();
    case 'cart':
      return renderCart();
    case 'checkout':
      return renderCheckout();
    case 'confirmation':
      return renderConfirmation();
    default:
      return renderProducts();
  }
}

export default App;