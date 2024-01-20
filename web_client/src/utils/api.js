let timer = null;

class API{
    constructor()
    {
        this.category_id = "";
        this.msg_id = "";
    }

    async get(params)
    {
        console.log(`api.php?${new URLSearchParams(params).toString()}`);
        return await fetch(`/api/${params["mode"]}?${new URLSearchParams(params).toString()}`);
    }

    async post(params) {
        console.log("post", params);
        return await fetch(`/api/${params["mode"]}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });
    }

    async whisper_api(file) {
        let api_url = "https://api.openai.com/v1/audio/transcriptions";
        let api_key = document.querySelector("#api_key").value;

        var formData = new FormData();
        formData.append('model', 'whisper-1');
        formData.append('file', file);
    
        const abortController = new AbortController();
        const param = {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${api_key}`
            },
            body: formData,
            signal: abortController.signal
        };
        for (let i = 0; i < 5; i++) {
            try {
                const response = await fetch(api_url, param);
                if (timer)
                    clearTimeout(timer);
                console.log(response);
                if (response.ok) {
                    return await response.json();
                }
                throw new Error(response.status);
            } catch (error) {
                if (error.name === 'AbortError') {
                    console.log("timeout for whisper", i);
                    timer = setTimeout(() => abortController.abort(), 3000);
                } else {
                    console.log(error);
                    return {};
                }
            }
        }
        return {};
    }
}

export const api = new API();
