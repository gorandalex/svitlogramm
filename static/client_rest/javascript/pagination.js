const previousBtn = document.getElementById('previousBtn');
const nextBtn = document.getElementById('nextBtn');

previousBtn.addEventListener('click', navigateToPreviousPage);
nextBtn.addEventListener('click', navigateToNextPage);

function navigateToPreviousPage() {
  const currentPageNumber = getCurrentPageNumber();
  const previousPageNumber = currentPageNumber - 1;
  navigateToPage(previousPageNumber);
}

function navigateToNextPage() {
  const currentPageNumber = getCurrentPageNumber();
  const nextPageNumber = currentPageNumber + 1;
  navigateToPage(nextPageNumber);
}

function getCurrentPageNumber() {
  // Ваш код для получения текущего номера страницы
  // Например, извлечение номера страницы из URL или из другого места
  // и возврат текущего номера страницы в виде числа
  // Замените этот код соответствующим способом получения текущего номера страницы
  return 1;
}

function navigateToPage(pageNumber) {
  const url = `{% url 'quotes:quotes_paginate' ${pageNumber} %}`;
  window.location.href = url;
}
