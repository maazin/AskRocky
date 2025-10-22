import bot from './assets/bot.svg'
import user from './assets/user.png'

const form = document.querySelector('form')
const chatContainer = document.querySelector('#chat_container')

let loadInterval

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}


function loader(element) {
    element.textContent = ''

    loadInterval = setInterval(() => {
        // Update the text content of the loading indicator
        element.textContent += '.';

        // If the loading indicator has reached three dots, reset it
        if (element.textContent === '....') {
            element.textContent = '';
        }
    }, 300);
}

function typeText(element, text, sources, titles) {
    let index = 0

    let interval = setInterval(() => {
        if (index < text.length) {
            element.innerHTML += text.charAt(index)
            index++
            scrollToBottom()
        } else {
            clearInterval(interval)
            element.innerHTML += typeLinks(sources, titles)
        }
    }, 5)
}

function typeLinks(links, titles) {
    let linksDivs = '';
    for (let i = 0; i < links.length && i<=3 ; i++) {
        linksDivs += `<div class="links-element">${i + 1}. <a href="${links[i]}" target="_blank">${titles[i]}</a></div>`;
    }
    return (
        `
        <div class="links">${linksDivs}</div>
        `
    )
}
// generate unique ID for each message div of bot
// necessary for typing text effect for that specific reply
// without unique ID, typing text will work on every element
function generateUniqueId() {
    const timestamp = Date.now();
    const randomNumber = Math.random();
    const hexadecimalString = randomNumber.toString(16);

    return `id-${timestamp}-${hexadecimalString}`;
}

function chatStripe(isAi, value, uniqueId) {
    return (
        `
        <div class="wrapper ${isAi && 'ai'}">
            <div class="chat">
                <div class="profile">
                    <img 
                      src=${isAi ? bot : user} 
                      alt="${isAi ? 'bot' : 'user'}" 
                    />
                </div>
                <div class="message" id=${uniqueId}>${value}</div>
            </div>
        </div>
    `
    )
}

function buttonStripe(buttonLabels) {
    return (
        `
        <div class="button-container">
            ${buttonLabels.map(label => `<button class="button-question">${label}</button>`).join('')}
        </div>
        `
    )
}

chatContainer.innerHTML += chatStripe(true, "Greetings! I'm the University of South Florida's official chatbot. How can I assist you today?");

const buttonLabels = [
    'What is USF and what campuses does it have?',
    'How do I apply? Deadlines and requirements?',
    'What programs and majors are available?'
];

chatContainer.innerHTML += buttonStripe(buttonLabels);

const buttonContainers = document.querySelectorAll('.button-question');

const handleSubmit = async (e, prompt) => {
    e.preventDefault()

    const data = new FormData(form)

    // user's chatstripe
    if (! prompt) {
        chatContainer.innerHTML += chatStripe(false, data.get('prompt'))
    } else {
        chatContainer.innerHTML += chatStripe(false, prompt)
    }
    // to clear the textarea input 
    form.reset()

    // bot's chatstripe
    const uniqueId = generateUniqueId()
    chatContainer.innerHTML += chatStripe(true, " ", uniqueId)

    // to focus scroll to the bottom 
    scrollToBottom()

    // specific message div 
    const messageDiv = document.getElementById(uniqueId)

    // messageDiv.innerHTML = "..."
    loader(messageDiv)
    const response = await fetch(import.meta.env.VITE_SERVER, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prompt: prompt || data.get('prompt')
        })
    })

    clearInterval(loadInterval)
    messageDiv.innerHTML = " "

    if (response.ok) {
        const data = await response.json();

        typeText(messageDiv, data.bot['result'], data.bot['source'], data.bot['title'])

    } else {
        const err = await response.text()

        messageDiv.innerHTML = "Continue after a few second. I'm taking a break!"
        console.log(err)
    }
}

buttonContainers.forEach((button) => {
    button.addEventListener('click', (e) => {
        const prompt = e.target.textContent;
        handleSubmit(e, prompt);
    });
}); 

form.addEventListener('submit', handleSubmit)
form.addEventListener('keyup', (e) => {
    if (e.keyCode === 13) {
        handleSubmit(e)
    }
})