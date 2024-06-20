$(document).ready(function () {
    $('#data-table').DataTable({
        // 日本語表示
        "language": {
            "url": "http://cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/Japanese.json",            
        },
        pageLength: 50,
    });
    $('#handshake').click(function() {
        console.log('クリックされました！');
        document.querySelector('[data-bs-target="#flush-collapseThree1"]').click();
    })
    $('#creditcard').click(function() {
        console.log('クリックされました！');
        document.querySelector('[data-bs-target="#flush-collapseThree2"]').click();
    })
    $('#bell').click(function() {
        console.log('クリックされました！');
        document.querySelector('[data-bs-target="#flush-collapseThree3"]').click();
    })
});
