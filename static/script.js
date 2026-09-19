const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const resultsContainer = document.getElementById("results-container");
const errorContainer = document.getElementById("error-container");


searchForm.addEventListener("submit", async function (event) {

    // Stop the browser from doing a normal form submission
    event.preventDefault();

    const query = searchInput.value.trim();

    // Clear old messages/results
    errorContainer.textContent = "";
    resultsContainer.innerHTML = "";

    if (!query) {
        errorContainer.textContent = "Please enter something to search for.";
        return;
    }

    try {

        const response = await fetch(
            "/api/search?page=1",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    query: query
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            errorContainer.textContent =
                data.error || "Something went wrong.";

            return;
        }

        for (let index = 0; index < data.results.length; index++) {

            const result = data.results[index];

            const resultCard = document.createElement("div");
            resultCard.className = "result-card";

            const title = document.createElement("h3");
            title.textContent =
                `${index + 1}. ${result.title}`;

            const link = document.createElement("a");
            link.href = result.link;
            link.target = "_blank";
            link.textContent = result.link;

            const linkParagraph = document.createElement("p");
            linkParagraph.appendChild(link);

            const snippet = document.createElement("p");
            snippet.textContent = result.snippet;

            resultCard.appendChild(title);
            resultCard.appendChild(linkParagraph);
            resultCard.appendChild(snippet);

            resultsContainer.appendChild(resultCard);
        }

    } catch (error) {

        errorContainer.textContent =
            "Could not connect to the API.";
    }
});