import '../css/styles.css';
import 'flowbite';
import Splide from '@splidejs/splide';

import * as JsCookie from "js-cookie";

import 'htmx.org';

export const Cookies = JsCookie.default;


// Splide themes
import '@splidejs/splide/css';
// import '@splidejs/splide/css/sea-green';
// import '@splidejs/splide/css/skyblue';
// import '@splidejs/splide/css/core';


document.addEventListener("DOMContentLoaded", function () {
    const csrftoken = Cookies.get("csrftoken")


    const megaMenuTrigger = document.getElementById("mega-menu-trigger");
    const megaMenu = document.getElementById("mega-menu");

    if (megaMenuTrigger) {
        megaMenuTrigger.addEventListener("click", () => {
            showMegaMenu();
        });
    }

    const showMegaMenu = () => {
        if (megaMenu) {
            if (megaMenu.classList.contains("show")) {
                megaMenu.classList.remove("show");
                megaMenuTrigger.classList.remove("active");
            } else {
                megaMenu.classList.add("show");
                megaMenuTrigger.classList.add("active");
            }
        }
    };

    document.addEventListener("click", (e) => {
        if (megaMenu) {
            if (
                megaMenu.classList.contains("show") &&
                !megaMenu.contains(e.target) &&
                !megaMenuTrigger.contains(e.target)
            ) {
                megaMenu.classList.remove("show");
                megaMenuTrigger.classList.remove("active");
            }
        }
    });

    // === Shopping Cart ===
    async function updateCartItem(id, action) {
        const url = cartItemsUrl.replace(0, id);
        const prepData = JSON.stringify({action, amount: 1});

        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                method: 'PATCH',
                body: prepData,
            });

            const data = await response.json();
            if (response.ok) {
                return data;
            } else {
                console.error('Error updating cart item:', data);
                alert(`Failed to update cart item: ${data.details || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Network error:', error);
            alert('A network error occurred. Please try again.');
        }

        return null;
    }

    async function handleQuantityUpdate(e, action) {
        const btn = e.currentTarget;
        const id = btn.getAttribute('data-id');
        const maxQuantity = Number(btn.getAttribute('data-max'));
        const quantityElement = document.getElementById(`cart-item-quantity-${id}`);
        const originalPriceElement = document.getElementById(`span-original-price`);
        const totalPriceElement = document.getElementById(`span-total-price`);
        const currentQuantity = Number(quantityElement.innerText);

        if (action === 'increase' && currentQuantity >= maxQuantity) {
            alert(`Maximum quantity of ${maxQuantity} reached for this item.`);
            return;
        }

        const data = await updateCartItem(id, action);
        if (data) {
            if (data?.deleted === true) {
                const cartItemElement = document.getElementById(`cart-item-${id}`);
                if (cartItemElement) {
                    cartItemElement.remove();
                }
            } else {
                quantityElement.innerText = data?.quantity;
            }

            originalPriceElement.innerText = data?.display_price
            totalPriceElement.innerText = data?.display_price

        }
    }

    document.querySelectorAll('.btn-cart-item-increase').forEach(btn => {
        btn.addEventListener('click', (e) => handleQuantityUpdate(e, 'increase'));
    });

    document.querySelectorAll('.btn-cart-item-decrease').forEach(btn => {
        btn.addEventListener('click', (e) => handleQuantityUpdate(e, 'decrease'));
    });

    async function removeCartItem(e) {
        const btn = e.currentTarget;
        const id = btn.getAttribute('data-id');
        const url = cartItemsUrl.replace(0, id);

        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json',
                },
            });

            if (response.status === 204) {
                const cartItemElement = document.getElementById(`cart-item-${id}`);
                if (cartItemElement) {
                    cartItemElement.remove();
                }
            } else {
                const data = await response.json();
                console.error('Error deleting cart item:', data.details || 'Unknown error');
                alert(`Failed to delete cart item: ${data.details || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Network error:', error);
            alert('A network error occurred. Please try again.');
        }
    }

    document.querySelectorAll('.btn-cart-item-remove').forEach(btn => {
        btn.addEventListener('click', removeCartItem);
    });


    // === Product Page ===
    if (document.querySelector('#product-slider-main') && document.querySelector('#product-thumbnail-slider')) {
        const mainProductSlider = new Splide('#product-slider-main', {
            fixedHeight: 500,
            // type: 'fade',
            heightRatio: 1,
            pagination: false,
            arrows: false,
            cover: true,
            gap: 10
        });
        const productThumbnailsSlider = new Splide('#product-thumbnail-slider', {
            rewind: true,
            fixedWidth: 80,
            fixedHeight: 80,
            isNavigation: true,
            gap: 10,
            focus: '',
            pagination: false,
            cover: true,
            dragMinThreshold: {
                mouse: 4,
                touch: 10,
            },
            breakpoints: {
                640: {
                    fixedWidth: 60,
                    fixedHeight: 60,
                },
            },
        });
        mainProductSlider.sync(productThumbnailsSlider);
        mainProductSlider.mount();
        productThumbnailsSlider.mount();
    }
});
