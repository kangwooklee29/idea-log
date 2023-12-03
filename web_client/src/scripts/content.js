import {api} from "../utils/api.js";

class Content {
    constructor($target)
    {
        this.$target = $target;
        this.data = [];
        this.content_of_now_category_obj = null;
        this.message_obj = {};
        this.category_id = api.category_id;
        $target.addEventListener("click", e=>{
            if (e.target.nodeName === "BUTTON")
            {
                if (e.target.classList.contains("up"))
                    this.move_this_msg(e.target, "up");
                else if (e.target.classList.contains("down"))
                    this.move_this_msg(e.target, "down");
                else if (e.target.classList.contains("reply"))
                    this.open_reply(e.target.parentNode);
                else if (e.target.classList.contains("delete"))
                    this.delete_msg(e.target.parentNode.parentNode.id.replace("msg_", ""));
            }
        });

        $target.addEventListener("mousedown", ()=>{this.click_start = Date.now()});
        $target.addEventListener("touchstart", ()=>{this.click_start = Date.now()});
        $target.addEventListener("mouseup", e=>{
            if (e.target.nodeName === "DIV" && e.target.classList.contains("message_inner"))
            {
                if (Date.now() - this.click_start > 800)
                    this.edit_msg(e.target);
                else
                    this.edit_category(e.target);
            }
        });
        $target.addEventListener("touchend", ()=>{
            if (e.target.nodeName === "DIV" && e.target.classList.contains("message_inner"))
            {
                if (Date.now() - this.click_start > 800)
                    this.edit_msg(e.target);
                else
                    this.edit_category(e.target);
            }
        });

        this.show();
        this.get_data({msg_id: api.msg_id});
    }

    open_reply(target)
    {

    }

    delete_msg(msg_id, category_id=localStorage.getItem('deleted_category_id')) // 카테고리 옮기고, 옮겨진 메시지는 그 자식과 함께 현재 DOM에서 제거.
    {
        api.post({mode:"write_message", category_id:category_id, msg_id:msg_id})
        .then(response=>{
            if (response.ok)
            {
                var q = [], qs=0;
                q.push(msg_id);
                while (qs < q.length)
                {
                    var node = document.querySelector(`div[id='msg_${q[qs]}']`)
                    console.log(node, q, msg_id);
                    if (node) this.content_of_now_category_obj.removeChild(node);
                    Array.from(document.querySelectorAll(`div[parent_msg_id='${q[qs]}']`)).forEach(elem => q.push(elem.id.replace("msg_", "")));
                    qs++;
                }
                return;
            }
            throw new Error("Request failed. Try again.");
        }).catch(error=>{
            alert(error);
        });
    }

    show()
    {
        this.content_of_now_category_obj = document.createElement("div");
        this.content_of_now_category_obj.classList.add("content_inner");
        
        if (this.$target.childNodes.length > 0) this.$target.removeChild(this.$target.firstChild);
        this.$target.appendChild(this.content_of_now_category_obj);
    }

    async get_data({parent_msg_id=-1, target_date="", limit=20, msg_id=null}={}) {
        if (parent_msg_id !== -1)
            limit = -1;

        var response = await api.get({
            mode: "fetch_messages",
            category_id: this.category_id,
            target_date: target_date,
            parent_msg_id: parent_msg_id,
            limit: limit,
            msg_id: msg_id
        });

        var res_json = null;
        if (response.ok) {
            try {
                res_json = await response.json();
            }
            catch(e) {
                console.log(response, `${parent_msg_id}, ${target_date}, ${limit, msg_id}`);
            }
        }
        else
            throw new Error("Request failed. Try again.");

        // 예를 들어 현재 content_inner의 높이가 100이고 현재 스크롤바의 위치가 30이라면, now_scroll에는 70이란 값이 저장됨.
        // 이후 예를들어 content_inner가 현재 위치에서 높이가 100이 추가돼 200이 됐다면, 원래는 스크롤바 위치는 그대로 30에서 변하지 않으나,
        // 밑에 연산을 통해 스크롤바 위치가 130으로 늘어남. 
        var now_scroll = this.content_of_now_category_obj.scrollHeight - this.content_of_now_category_obj.scrollTop;

        if (res_json && Object.keys(res_json).length !== 0) {
            res_json.forEach(async elem => {
                var new_msg_obj = this.make_new_msg_obj(elem);

                if (limit === 1) {
                }
                else {
                    if (parent_msg_id === -1) {
                        if (this.content_of_now_category_obj.childNodes.length > 0)
                            this.content_of_now_category_obj.insertBefore(new_msg_obj, this.content_of_now_category_obj.firstChild);
                        else
                            this.content_of_now_category_obj.appendChild(new_msg_obj);
                    }
                    else { //현재, 주어진 부모의 자식 메시지들을 sql 쿼리로 받아와서 DOM에 추가해야 하는 상황. 
                        var parent_obj = this.content_of_now_category_obj.querySelector(`div[id="msg_${parent_msg_id}"]`);
                        parent_obj.appendChild(new_msg_obj);
                        new_msg_obj.style.left =  (parseInt(parent_obj.style.left) + 20) + "px";
                        new_msg_obj.style.width = (parent_obj.offsetWidth - 20) + "px";
                    }    
                    if (elem['msg_id'])
                        await this.get_data({parent_msg_id: elem['msg_id']});
                }
            });

/*

msg_id !== null 인 케이스에 관한 구현.

1. 이 값이 null이면, 그냥 기존 프로세스대로 처리한다.

2. 이 값이 null이 아니면, 검색 클릭 사례거나 새로 메시지/댓글이 추가된 사례인 거. 

- 그 메시지가 스크린 최상단에 올 수 있게 해야.

- 얻어오는 메시지 개수는 그 메시지 번호 기준 위로 10개, 아래로 10개.

- 위에 10번째, 아래 10번째 메시지에는 observe 붙여줘야. 



*/



            window.parent.document.querySelector("iframe").contentDocument.documentElement.scrollTop = target_date ? this.content_of_now_category_obj.scrollHeight - now_scroll : this.content_of_now_category_obj.scrollHeight; 

            if (Object.keys(res_json).length === 20)
            {
                let io = new IntersectionObserver( entries =>
                    {
                        entries.forEach(async entry => 
                        {
                            if (entry.isIntersecting) 
                            {
                                console.log(entry.target);
                                io.unobserve(entry.target);
                                await this.get_data({target_date:res_json[res_json.length-1]['written_date']});
                            }
                        });
                    });
                io.observe(this.content_of_now_category_obj.firstChild);
            }
        }
    }

    make_new_msg_obj(elem)
    {
        /*

        div.message_outer
            div.message_inner
                #text
            div.msg_controller
                span.written_date
                button.up
                button.down

        '댓글달기' 버튼 만들고 댓글란 보여주고 업데이트 부분 api 구현해야 함. 

        */
        const msg_outer_obj = document.createElement("div");
        msg_outer_obj.classList.add("message_outer");
        msg_outer_obj.id = ("msg_id" in elem) ? `msg_${elem['msg_id']}` : "";
        if ("parent_msg_id" in elem)
            msg_outer_obj.setAttribute("parent_msg_id", elem['parent_msg_id']);
        msg_outer_obj.setAttribute("written_date", elem['written_date']);

        const msg_controller_obj = document.createElement("div");
        var date = new Date(parseInt(elem['written_date']));
        var time_str = ('0' + date.getHours()).slice(-2) + ':' + ('0' + date.getMinutes()).slice(-2);
        var date_str = `${date.getFullYear()}-${date.getMonth()+1}-${date.getDate()}`;

        const msg_inner_obj = document.createElement("div");
        msg_inner_obj.classList.add("message_inner");
        msg_inner_obj.innerHTML = `<div class="date_str">${date_str}</div>${this.make_message_appropriate(elem['message'])}<span style="font-size:1pt;color:white;">${date_str} ${time_str}</span><button class="reply">+</button><button class="delete">x</button>`;
        msg_outer_obj.appendChild(msg_inner_obj);

        msg_controller_obj.classList.add("msg_controller");
        msg_controller_obj.innerHTML = `<button class="up">▲</button><button class="down">▼</button><span>${time_str}</span>`;
        msg_outer_obj.appendChild(msg_controller_obj);
        return msg_outer_obj;
    }

    make_message_appropriate(message)
    {
        message = message.replace(">", "&gt;").replace("<", "&lt;");
        var split_by_https = message.split("https://");
        if (split_by_https.length > 1)
        {
            const href = split_by_https[1].split(/["') \n]/);
            message = `${split_by_https[0]}<a href="https://${href[0]}" target="_blank">https://${href[0]}</a>${split_by_https[1].replace(href[0], "")}`;
        }
        return `<pre>${message}</pre>`;
    }

    get_msg_id(target)
    {
        while (target && target.nodeName !== "div" && target.classList.contains("message_outer") === false)
            target = target.parentNode;
        return (target && target.nodeName === "div" && target.classList.contains("message_outer")) ? target.id : null;
    }

    move_this_msg(target, dir)
    {
        var id = this.get_msg_id(target);
        var msg_obj = this.content_of_now_category_obj.querySelector(`div[id="${id}"]`);
        var msg_objs = this.content_of_now_category_obj.childNodes;
        var i = null;

        msg_objs.forEach((elem, k) => {if (elem === msg_obj) i = k;});

/*

- ...
- ...
  - ...
    - ...
    - ...
      - ...
    - ...

1. 바닥에 있던 녀석은 바로 위 타래의 마지막 자식으로 올릴 필요가 있음.

2. 거기서 더 위로 버튼을 눌렀을 때 어떤 액션을 취해야 하는가..
- 원하는 시나리오는 이거.
1) 일단, 바로 위 인덱스 자식으로 보낸다.
2) 이미 바로 위 인덱스 자식이라면, 그보다 위 인덱스 자식으로 올려보낸다.
3) 근데 그보다 위 인덱스가 현재 바로 위의 부모라면, 그보다 위 인덱스 자식으로 올려보낸다.
...

왜케 어렵냐 ㅠ


*/

        if (dir === "up" && i) 
        {
            var find_next_parent = i-1;
            for (var j=i-2; j>=0; j--)
            {
                if (msg_objs[find_next_parent].parent_msg_id !== msg_objs[j].msg_id)
                    break;
                find_next_parent = j;
            }

            api.get({mode:"move_message", idx_child: id, idx_parent:msg_objs[find_next_parent].id})
            .then(()=>{
                if (response.ok)
                {
                    msg_objs.forEach(elem=>{
                        if (elem.parent_msg_id === find_next_parent)
                            this.content_of_now_category_obj.removeChild(elem); 
                    })
                    this.get_data({parent_msg_id: find_next_parent});
                    return;
                }
                throw new Error("Request failed. Try again.");
            }).catch(error=>{
                alert(error);
            });
        }
        else if(dir === "down" && i != msg_objs.length-1) //현재 부모와의 관계를 종료하고 현재 부모의 부모의 자식으로 붙여줘야.
        {
            var find_next_parent = document.querySelector(`div[id="msg_${msg_objs[i].parent_msg_id}"]`).parent_msg_id;
            api.get({mode:"move_message", idx_child: id, idx_parent:find_next_parent})
            .then(()=>{
                if (response.ok)
                {
                    msg_objs.forEach(elem=>{
                        if (elem.parent_msg_id === find_next_parent)
                            this.content_of_now_category_obj.removeChild(elem); 
                    })
                    this.get_data({parent_msg_id: find_next_parent});                    
                    return;
                }
                throw new Error("Request failed. Try again.");
            }).catch(error=>{
                alert(error);
            })
        }
    }

    edit_category(target) //살짝 터치 시 카테고리 수정. 만약 수정요청이 자식이라면 거절하고, 부모라면 모든 자식 함께 이동해야.
    {
        var id = this.get_msg_id(target);
        //카테고리 수정할 수 있는 모달을 띄워야... 걍 타이틀 복붙하면 될 듯? 
    }

    edit_msg(target) //길게 터치 시 내용 수정
    {
        var id = this.get_msg_id(target);
        //그냥 메시지 안에 textarea랑 수정완료 버튼 넣으면 됨
    }
}

api.category_id = localStorage.getItem('content_category_id');
new Content(document.querySelector("main"));
