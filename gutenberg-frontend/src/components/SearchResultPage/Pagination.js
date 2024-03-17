const PaginationElem = ({ booksPerPage, totalBooks, paginate, currentPage }) => {
    const pageNumbers = [];
    const totalPages = Math.ceil(totalBooks / booksPerPage);
    const pagesToShow = 15; // Total pages you want to display in the pagination
    const halfPagesToShow = Math.floor(pagesToShow / 2);

    let startPage = Math.max(currentPage - halfPagesToShow, 1);
    let endPage = Math.min(startPage + pagesToShow - 1, totalPages);

    if (endPage - startPage < pagesToShow - 1) {
        startPage = Math.max(1, endPage - pagesToShow + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        pageNumbers.push(i);
    }

    return (
        <nav>
            <ul className='pagination'>
                <li className='page-item'>
                    <button onClick={() => paginate(1)} disabled={currentPage === 1}>&laquo;&laquo;</button>
                </li>
                <li className='page-item'>
                    <button onClick={() => paginate(Math.max(currentPage - 1, 1))} disabled={currentPage === 1}>&laquo;</button>
                </li>
                {pageNumbers.map(number => (
                    <li key={number} className={'page-item' + (number === currentPage ? ' active' : '')}>
                        <button onClick={() => paginate(number)} className='page-link'>
                            {number}
                        </button>
                    </li>
                ))}
                <li className='page-item'>
                    <button onClick={() => paginate(Math.min(currentPage + 1, totalPages))} disabled={currentPage === totalPages}>&raquo;</button>
                </li>
                <li className='page-item'>
                    <button onClick={() => paginate(totalPages)} disabled={currentPage === totalPages}>&raquo;&raquo;</button>
                </li>
            </ul>
        </nav>
    );
};
export default PaginationElem;