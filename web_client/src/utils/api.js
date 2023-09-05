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
}

export const api = new API();
