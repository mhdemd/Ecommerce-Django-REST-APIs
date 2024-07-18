
// product-control.js

// Add an event listener to size and color radio buttons
const sizeRadioButtons = document.querySelectorAll('input[type="radio"][name="size"]');
const colorRadioButtons = document.querySelectorAll('input[type="radio"][name="color"]');
const productPriceElement = document.getElementById('product-price');

sizeRadioButtons.forEach(radio => {
radio.addEventListener('change', updateProductPrice);
});

colorRadioButtons.forEach(radio => {
radio.addEventListener('change', updateProductPrice);
});

function updateProductPrice() {
const selectedSizeRadio = document.querySelector('input[type="radio"][name="size"]:checked');
const selectedColorRadio = document.querySelector('input[type="radio"][name="color"]:checked');

const selectedSizePrice = selectedSizeRadio ? selectedSizeRadio.getAttribute('data-price') : 0;
const selectedColorPrice = selectedColorRadio ? selectedColorRadio.getAttribute('data-price') : 0;

const totalPrice = parseFloat(selectedSizePrice) + parseFloat(selectedColorPrice);

productPriceElement.textContent = '$ ' + totalPrice.toFixed(2);
}

// Initialize the product price based on the initial selection
updateProductPrice();
