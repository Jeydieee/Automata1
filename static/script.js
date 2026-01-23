document.addEventListener("DOMContentLoaded", function() {
    // Only fetch history if we are on the main page (optional, but good for performance)
    // Or we can just let the advanced page handle history.
    if(document.getElementById('historyList') && !document.getElementById('automataLog')) {
        // If we are on a page with history but NOT logs (rare case with this setup, but safe)
        fetchHistory();
    }
});

async function scanMessage() {
    const message = document.getElementById('messageInput').value;
    const resultCard = document.getElementById('resultCard');
    const badge = document.getElementById('resultBadge');

    if (!message) return alert("Please enter a message!");

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        resultCard.style.display = 'block';

        // Update Badge
        if (data.is_spam) {
            badge.className = "badge spam";
            badge.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${data.classification}`;
        } else {
            badge.className = "badge safe";
            badge.innerHTML = `<i class="fas fa-check-circle"></i> ${data.classification}`;
        }

        // Update Stats
        document.getElementById('keywordsFound').innerText = data.patterns_found.length > 0 ? data.patterns_found.join(", ") : "None";
        document.getElementById('riskScore').innerText = data.heuristic_score + "%";

        // SAVE LOGS TO LOCAL STORAGE FOR THE ADVANCED PAGE
        localStorage.setItem('lastScanLogs', JSON.stringify(data.automata_logs));

    } catch (error) {
        console.error("Error:", error);
        alert("Something went wrong! Check the Console (F12) for details.");
    }
}

// Function called specifically by advanced.html
function initAdvancedPage() {
    fetchHistory();
    
    // Retrieve logs from the last scan
    const storedLogs = localStorage.getItem('lastScanLogs');
    if (storedLogs) {
        const logs = JSON.parse(storedLogs);
        visualizeAutomata(logs);
    }
}

function visualizeAutomata(logs) {
    const container = document.getElementById('automataLog');
    if (!container) return; // Guard clause in case function is called on index page

    container.innerHTML = ""; // Clear previous

    if (!logs || logs.length === 0) {
        container.innerHTML = "<p>No transition data available.</p>";
        return;
    }

    logs.forEach((log, index) => {
        const div = document.createElement('div');
        div.className = 'step';

        let arrow = "→";
        let color = "#34D399"; // Green for normal transition

        if (log.status.includes("MATCH")) color = "#EF4444"; // Red for match
        if (log.status === "Reset") color = "#6B7280"; // Grey for reset

        div.innerHTML = `
            <span style="color:#aaa">[${index}]</span> 
            State <strong>${log.from_state}</strong> 
            + Input '<strong>${log.char}</strong>' 
            ${arrow} State <strong>${log.to_state}</strong> 
            <span style="color:${color}">(${log.status})</span>
        `;
        container.appendChild(div);
    });
}

async function fetchHistory() {
    try {
        const list = document.getElementById('historyList');
        if (!list) return; // Exit if element doesn't exist

        const response = await fetch('/history');
        if (!response.ok) return;

        const data = await response.json();
        list.innerHTML = "";

        data.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${item[1]}</strong>: "${item[0].substring(0, 30)}..." <br><small>${item[3]}</small>`;
            list.appendChild(li);
        });
    } catch (error) {
        console.log("Could not fetch history:", error);
    }
}