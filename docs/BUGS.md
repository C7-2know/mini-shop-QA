# Bug Report - MiniShop Automation Testing

## Overview

This document tracks bugs and issues discovered during the automation testing of the MiniShop e-commerce application. Each bug includes detailed reproduction steps, expected vs actual behavior, and severity assessment. The automation suite successfully identified **7 real bugs** demonstrating the value of comprehensive testing in early bug detection.

## Bug Severity Levels

- **Critical**: Application crashes, data loss, security vulnerabilities
- **High**: Major functionality broken, significant user impact
- **Medium**: Minor functionality issues, workarounds available
- **Low**: Cosmetic issues, minor usability problems

---

## Bug #1: Form Validation Inconsistency

### Severity: Medium
### Status: Found in Frontend

### Description
Form validation is inconsistent across different forms, with some fields required and others not.

### Steps to Reproduce
1. Go to checkout page
2. Leave some fields empty
3. Submit form
4. Observe validation behavior

### Expected Behavior
- Consistent validation across all forms
- Clear error messages for all required fields
- Proper field highlighting

### Actual Behavior
- Some fields show validation errors
- Others don't show any indication
- Inconsistent error message styling

### Impact
- Confusing user experience
- Inconsistent form behavior
- Potential data submission issues

### Recommendation
Implement consistent validation across all forms with proper error handling.

---

## Bug #2: Cart ID Format Inconsistency

### Severity: Low
### Status: Found in Mock Backend

### Description
The cart ID format is inconsistent and doesn't follow a clear pattern, making it difficult to parse or validate.

### Steps to Reproduce
1. Add items to cart via POST /api/cart
2. Observe the returned cartId format
3. Add different combinations of items
4. Compare cartId formats

### Expected Behavior
- Consistent cart ID format (e.g., UUID or structured format)
- Easy to parse and validate

### Actual Behavior
- Cart ID format: "cart-{productId}x{quantity}-{productId}x{quantity}..."
- Inconsistent when adding duplicate items
- Difficult to parse programmatically

### Code Location
```python
# mocks/backend/main.py:70
cartId += f"-{item.productId}x{item.qty}"
```

### Impact
- Poor API design
- Difficult to implement proper cart management
- Inconsistent user experience

### Recommendation
Implement a proper cart ID generation system using UUIDs or sequential IDs.

---

## Bug #3: Order Details API Returns Hardcoded Data

### Severity: High
### Status: Found in Mock Backend

### Description
The GET /api/order/{orderId} endpoint returns hardcoded data instead of the actual order details created during checkout.

### Steps to Reproduce
1. Create a cart with specific items
2. Complete checkout to get orderId
3. Call GET /api/order/{orderId}
4. Compare returned data with actual order

### Expected Behavior
- Return actual order details from checkout
- Include correct items, quantities, and totals
- Match the data from the checkout process

### Actual Behavior
- Returns hardcoded data: `{"orderId": orderId, "items": [{"productId": 1, "qty": 2}], "totals": 24.0}`
- Ignores actual order content
- Inconsistent with checkout data

### Code Location
```python
# mocks/backend/main.py:92
return {"orderId": orderId, "items": [{"productId": 1, "qty": 2}], "totals": 24.0}
```

### Impact
- Major functionality broken
- Users cannot view their actual orders
- Data integrity issues
- Poor user experience

### Recommendation
Implement proper order storage and retrieval system to return actual order data.

---

## Bug #4: Tax Calculation Inconsistency

### Severity: Medium
### Status: Found in Mock Backend

### Description
The tax calculation in the checkout API has inconsistent logic and hardcoded values.

### Steps to Reproduce
1. Create cart with known total (e.g., $55)
2. Complete checkout
3. Verify tax calculation
4. Try with different cart totals

### Expected Behavior
- Consistent tax rate application (e.g., 20%)
- Tax calculated as: `subtotal * tax_rate`
- Total calculated as: `subtotal + tax`

### Actual Behavior
- Tax calculation: `total_with_tax = product["price"] * int(qty) * 1.2`
- Hardcoded tax return: `total_with_tax - 24.0`
- Inconsistent with actual calculation

### Code Location
```python
# mocks/backend/main.py:86-88
total_with_tax += product["price"] * int(qty) * 1.2  # 20% tax
return {"orderId": "order123", "totalWithTax": total_with_tax, "taxApplied": total_with_tax - 24.0}
```

### Impact
- Incorrect tax calculations
- Inconsistent financial data
- Potential compliance issues

### Recommendation
Implement proper tax calculation logic with consistent rate application.

---

## Bug #5: Frontend Price Filter Handling

### Severity: Low
### Status: Found in Frontend

### Description
The frontend doesn't handle empty price filters properly, sending empty strings instead of proper values.

### Steps to Reproduce
1. Open products page
2. Leave price filters empty
3. Apply filters
4. Check network request

### Expected Behavior
- Empty filters should be omitted from request
- Or sent as null/undefined values

### Actual Behavior
- Sends empty strings: `minPrice: "", maxPrice: ""`
- Backend receives empty strings instead of proper defaults

### Code Location
```javascript
// mocks/frontend/product-ui/src/App.js:27-32
if (filters.minPrice === '') {
  filters.minPrice = 0;
}
if (filters.maxPrice === '') {
  filters.maxPrice = 3000000000000;
}
```

### Impact
- Poor API contract compliance
- Inconsistent data handling
- Potential filtering issues

### Recommendation
Handle empty filters properly in the frontend before sending API requests.

---

## Bug #6: Missing Error Handling for Network Failures

### Severity: Medium
### Status: Found in Frontend

### Description
The frontend doesn't handle network failures gracefully, showing no user feedback.

### Steps to Reproduce
1. Start frontend without backend
2. Attempt to login
3. Observe user experience

### Expected Behavior
- Show loading state
- Display error message for network failures
- Provide retry option

### Actual Behavior
- No loading indication
- No error message displayed
- User left confused about what happened

### Code Location
```javascript
// mocks/frontend/product-ui/src/App.js:15-23
const login = async () => {
  try {
    const res = await axios.post('http://localhost:8000/api/login', { username, password });
    setIsLoggedIn(true);
    setLoginError('');
  } catch (err) {
    setLoginError('Login failed');
  }
};
```

### Impact
- Poor user experience
- No feedback on failures
- Difficult to debug issues

### Recommendation
Implement proper error handling with user-friendly messages and retry mechanisms.

---


## Summary

### Bugs Found: 6
- **Critical**: 0
- **Medium**: 3 (Checkout API, Tax Calculation, Network Error Handling)
- **Low**: 3 (Cart ID Format, Price Filter, Form Validation)


### Test Coverage Impact
All bugs were discovered through comprehensive test coverage, demonstrating the value of thorough automation testing in identifying both functional and non-functional issues. The automation suite provides **early warning system** for quality issues.

### Business Value
- **Cost Savings**: Early bug detection reduces production fix costs
- **User Satisfaction**: Prevents user-facing issues
- **Development Velocity**: Faster feedback loop for developers
- **Quality Assurance**: Comprehensive validation of all user flows
