// 資料狀態，DOM元素
const attractionsGrid = document.querySelector(".attractions__grid");
const observerTarget = document.querySelector(".observer");
const searchInput = document.querySelector(".search__input");
const searchBtn = document.querySelector(".search__btn");
const categoryBtn = document.querySelector(".category__btn");
const categoryPopup = document.querySelector(".category__popup");
const mrtList = document.querySelector(".mrt__list");
const mrtWrapper = document.querySelector(".mrt__list-wrapper");
const SCROLL_AMOUNT = 300;

// 建立一些會用到的變數
let nextPage = 0;
let isLoading = false;
let currentKeyword = "";
let currentCategory = "";

// render 把fetch過來的資料做畫面渲染
function renderAttractionCards(attractions){
    const fragment = document.createDocumentFragment();

    attractions.forEach(attraction => {
        const card = document.createElement("div");
        card.className = "attraction-card";

        card.innerHTML = `
           <div class="attraction-card__image">
            <img src="${attraction.images[0]}" alt="${attraction.name}">
            <div class="attraction-card__name">${attraction.name}</div>
           </div> 

           <div class="attraction-card__info">
            <span class="attraction-card__mrt">${attraction.mrt || ""}</span>
            <span class="attraction-card__category">${attraction.category}</span>
           </div>
        `;  

        fragment.appendChild(card);
    });

    attractionsGrid.appendChild(fragment);
}

// 共用 fetch function(nextPage對應)、拿資料
async function fetchAttractions() {
    if (isLoading || nextPage === null) return;

    isLoading = true;

    let url = `/api/attractions?page=${nextPage}`;

    if (currentKeyword) {
        url += `&keyword=${encodeURIComponent(currentKeyword)}`;
    }

    if(currentCategory) {
        url += `&category=${encodeURIComponent(currentCategory)}`;
    }

    try {
        const response = await fetch(url);
        const result = await response.json();
        
        renderAttractionCards(result.data);
        nextPage = result.nextPage;
    } catch (error) {
        console.error("Failed to fetch attractions:", error);
    } finally {
        isLoading = false;
    }
}
// 無限滾動區塊的設定
const intersectionObserver = new IntersectionObserver(
    entries => {
        const entry = entries[0];
        if (entry.isIntersecting) {
            fetchAttractions();
        }
    },
    {   
        root: null,
        rootMargin: "0px",
        threshold: 0.1 
    }
);

intersectionObserver.observe(observerTarget);

// 頁面的init
document.addEventListener("DOMContentLoaded", () => {
    fetchAttractions();
});

// 在搜尋/分類/MRT點擊時
function resetAttractions() {
    attractionsGrid.innerHTML = "";
    nextPage = 0;
}
// resetAttractions();
// fetchAttractions();

// Part 2-4~2-5 category&keyword篩選
function searchAttractions({ keyword = "", category = ""}) {
    currentKeyword = keyword;
    currentCategory = category;

    attractionsGrid.innerHTML = "";
    nextPage = 0;

    fetchAttractions();
}

searchBtn.addEventListener("click", () => {
    searchAttractions({
        keyword: searchInput.value.trim(),
        category: currentCategory
    });
});
// Enter送出按鍵設定
searchInput.addEventListener("keydown", e => {
    if (e.key === "Enter") {
        searchBtn.click();
    }
});

// 點選分類按鍵跳出
categoryBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    categoryPopup.classList.toggle("active");
});
categoryPopup.addEventListener("click", () => {
    e.stopPropagation();
});
document.addEventListener("click", () => {
    categoryPopup.classList.remove("active");
});

// 載入category
async function loadCategories() {
    const res = await fetch("/api/categories");
    const data = await res.json();

    categoryPopup.innerHTML = data.data
        .map(cat => `<div class="category-item">${cat}</div>`)
        .join("");
}
// 頁面載入時呼叫一次
loadCategories();

// 當點擊某個分類時，會進行搜尋
categoryPopup.addEventListener("click", e => {
    if (!e.target.classList.contains("category-item")) return;

    const selectedCategory = e.target.textContent;
    categoryBtn.textContent = `${selectedCategory} ▼ `;

    categoryPopup.classList.add("active");

    searchAttractions({
        keyword: "",
        category: selectedCategory
    });
});

// Part 2-6 MRT列表點擊
// MRT清單載入
async function loadMrts() {
    const res = await fetch("/api/mrts");
    const data = await res.json();

    mrtList.innerHTML = data.data
        .map(mrt => `<li class="mrt__item">${mrt}</li>`)
        .join("");
}

loadMrts();
// 點擊MRT選項，並搜尋
mrtList.addEventListener("click", e => {
    if (!e.target.classList.contains("mrt__item")) return;

    const mrtName = e.target.textContent;

    searchInput.value = mrtName;

    searchAttractions({
        keyword: mrtName,
        category: currentCategory
    });
});

document.querySelector(".mrt__arrow--left").addEventListener("click", () => {
    mrtWrapper.scrollLeft -= SCROLL_AMOUNT;
});
document.querySelector(".mrt__arrow--right").addEventListener("click", () => {
    mrtWrapper.scrollLeft += SCROLL_AMOUNT;
});