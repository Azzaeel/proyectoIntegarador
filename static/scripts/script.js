const select = document.getElementById('select')
const button = document.querySelector('button')

select.addEventListener('change', () => {
    button.disabled = false;
})

const selectProveedor = document.getElementsByName('proveedor')[0]
selectProveedor.addEventListener('change', () => {
    alert('Cambió esa mierda')
})