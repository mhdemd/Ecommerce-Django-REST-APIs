document.addEventListener('DOMContentLoaded', function () {
    const decreaseButton = document.querySelector('#decrease-quantity');
    const increaseButton = document.querySelector('#increase-quantity');
    const quantityInput = document.querySelector('#quantity');
    
    decreaseButton.addEventListener('click', function () {
        if (quantityInput.value > 1) {
            quantityInput.value--;
        }
    });

    increaseButton.addEventListener('click', function () {
        if (quantityInput.value < 100) {
            quantityInput.value++;
        }
    });
});
