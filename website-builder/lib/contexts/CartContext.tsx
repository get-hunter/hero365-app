'use client';

import { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { ShoppingCart, CartItem, CartSummary, MembershipType } from '@/lib/types/products';

interface CartContextType {
  cart: ShoppingCart | null;
  cartSummary: CartSummary | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  createCart: () => Promise<void>;
  addToCart: (item: AddCartItemRequest) => Promise<void>;
  updateCartItem: (itemId: string, quantity: number) => Promise<void>;
  removeFromCart: (itemId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  refreshCart: () => Promise<void>;
}

interface AddCartItemRequest {
  product_id: string;
  installation_option_id?: string;
  quantity: number;
  membership_type?: MembershipType;
}

interface CartState {
  cart: ShoppingCart | null;
  cartSummary: CartSummary | null;
  isLoading: boolean;
  error: string | null;
}

type CartAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_CART'; payload: ShoppingCart }
  | { type: 'SET_CART_SUMMARY'; payload: CartSummary }
  | { type: 'CLEAR_CART' };

const initialState: CartState = {
  cart: null,
  cartSummary: null,
  isLoading: false,
  error: null,
};

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'SET_CART':
      return { ...state, cart: action.payload, error: null, isLoading: false };
    case 'SET_CART_SUMMARY':
      return { ...state, cartSummary: action.payload };
    case 'CLEAR_CART':
      return { ...state, cart: null, cartSummary: null };
    default:
      return state;
  }
}

const CartContext = createContext<CartContextType | undefined>(undefined);

interface CartProviderProps {
  children: ReactNode;
  businessId: string;
}

export function CartProvider({ children, businessId }: CartProviderProps) {
  const [state, dispatch] = useReducer(cartReducer, initialState);

  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Get or create cart ID from localStorage
  const getCartId = (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('cart_id');
  };

  const setCartId = (cartId: string): void => {
    if (typeof window === 'undefined') return;
    localStorage.setItem('cart_id', cartId);
  };

  const removeCartId = (): void => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('cart_id');
  };

  const createCart = async (): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const sessionId = `session_${Date.now()}`;
      const response = await fetch(`${backendUrl}/api/v1/public/contractors/shopping-cart/create?session_id=${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to create cart: ${response.status} ${errorText}`);
      }

      const cart = await response.json();
      
      // Validate cart response has required ID
      if (!cart || !cart.id) {
        throw new Error('Invalid cart response: missing cart ID');
      }
      
      setCartId(cart.id);
      dispatch({ type: 'SET_CART', payload: cart });
      
      // Also get cart summary (but don't fail if this fails)
      try {
        await getCartSummary(cart.id);
      } catch (summaryError) {
        console.warn('Failed to load cart summary:', summaryError);
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create cart';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      // Re-throw the error so callers can handle it
      throw new Error(errorMessage);
    }
  };

  const getCartSummary = async (cartId: string): Promise<void> => {
    try {
      const response = await fetch(`${backendUrl}/api/v1/public/contractors/shopping-cart/${cartId}/summary`);
      
      if (response.ok) {
        const summary = await response.json();
        dispatch({ type: 'SET_CART_SUMMARY', payload: summary });
      }
    } catch (error) {
      console.error('Failed to fetch cart summary:', error);
    }
  };

  const refreshCart = async (): Promise<void> => {
    const cartId = getCartId();
    if (!cartId) {
      console.log('🛒 [CART-CONTEXT] refreshCart: No cart_id, skipping');
      return;
    }

    console.log('🛒 [CART-CONTEXT] refreshCart: Loading cart from API:', cartId);
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const response = await fetch(`${backendUrl}/api/v1/public/contractors/shopping-cart/${cartId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          console.log('🛒 [CART-CONTEXT] Cart not found (404), clearing localStorage');
          // Cart not found, clear local storage
          removeCartId();
          dispatch({ type: 'CLEAR_CART' });
          return;
        }
        throw new Error(`Failed to fetch cart: ${response.status} ${response.statusText}`);
      }

      const cart = await response.json();
      console.log('🛒 [CART-CONTEXT] Cart loaded successfully:', { 
        cartId: cart.id, 
        itemCount: cart.item_count, 
        items: cart.items?.length || 0 
      });
      dispatch({ type: 'SET_CART', payload: cart });
      
      // Also get cart summary
      await getCartSummary(cartId);
    } catch (error) {
      console.error('🛒 [CART-CONTEXT] refreshCart error:', error);
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to fetch cart' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const addToCart = async (item: AddCartItemRequest): Promise<void> => {
    let cartId = getCartId();
    console.log('🛒 [CART-CONTEXT] addToCart called:', { item, currentCartId: cartId });
    
    // Create cart if it doesn't exist
    if (!cartId) {
      console.log('🛒 [CART] Creating new cart...');
      try {
        await createCart();
        cartId = getCartId();
        if (!cartId) {
          throw new Error('Cart creation succeeded but cart ID is still missing from localStorage');
        }
        console.log('✅ [CART] Cart created successfully:', cartId);
      } catch (error) {
        console.error('❌ [CART] Failed to create cart:', error);
        throw new Error(`Failed to create shopping cart: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }

    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      console.log('🛒 [CART] Adding item to cart:', cartId, item);
      const response = await fetch(`${backendUrl}/api/v1/public/contractors/shopping-cart/${cartId}/items?business_id=${businessId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ [CART] Add item failed:', response.status, errorText);
        throw new Error(`Failed to add item to cart: ${response.status} ${errorText}`);
      }

      console.log('✅ [CART] Item added successfully');
      // Refresh the cart to get updated data
      await refreshCart();
    } catch (error) {
      console.error('❌ [CART] Failed to add item:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to add item to cart';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      // Re-throw the error so UI components can handle it
      throw new Error(errorMessage);
    }
  };

  const updateCartItem = async (itemId: string, quantity: number): Promise<void> => {
    const cartId = getCartId();
    if (!cartId) return;

    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const response = await fetch(`${backendUrl}/api/v1/public/contractors/shopping-cart/${cartId}/items/${itemId}?quantity=${quantity}&business_id=${businessId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('Failed to update cart item');
      }

      // Refresh the cart to get updated data
      await refreshCart();
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to update cart item' });
    }
  };

  const removeFromCart = async (itemId: string): Promise<void> => {
    const cartId = getCartId();
    if (!cartId) return;

    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const response = await fetch(`${backendUrl}/api/v1/public/contractors/shopping-cart/${cartId}/items/${itemId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Failed to remove item from cart');
      }

      // Refresh the cart to get updated data
      await refreshCart();
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to remove item' });
    }
  };

  const clearCart = async (): Promise<void> => {
    const cartId = getCartId();
    if (!cartId) return;

    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const response = await fetch(`${backendUrl}/api/v1/public/contractors/shopping-cart/${cartId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Failed to clear cart');
      }

      removeCartId();
      dispatch({ type: 'CLEAR_CART' });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to clear cart' });
    }
  };

  // Load cart on mount
  useEffect(() => {
    const cartId = getCartId();
    console.log('🛒 [CART-CONTEXT] Initializing cart context:', { cartId, businessId });
    
    if (cartId) {
      console.log('🛒 [CART-CONTEXT] Found cart_id in localStorage, refreshing cart...');
      refreshCart();
    } else {
      console.log('🛒 [CART-CONTEXT] No cart_id in localStorage, starting with empty cart');
    }
  }, [businessId]);

  const value: CartContextType = {
    cart: state.cart,
    cartSummary: state.cartSummary,
    isLoading: state.isLoading,
    error: state.error,
    createCart,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    refreshCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
