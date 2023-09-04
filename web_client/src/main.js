import {api} from "./api.js";

class Title{
    constructor($target)
    {
        this.$target = $target;
        this.add_button_obj = $target.querySelector("button.add");
        this.add_button_hide();
        this.add_button_obj.addEventListener("click", ()=> this.add_category());
        this.all_button_obj = $target.querySelector("button.all");
        this.all_button_obj.addEventListener("click", () => { this.clear_input(); this.move_category(1); });

        this.input_obj = $target.querySelector("input");
        this.input_obj.addEventListener("focus", ()=>{this.clear_input(); this.show_categories();});
        this.input_obj.addEventListener("blur", ()=>setTimeout(()=>this.categories_hide(), 200));
        this.$target.addEventListener("keydown", (e) => {
            if (e.target === this.input_obj || e.target === this.categories_obj)
            {
                if (e.key == "Enter") 
                {
                    const buttons = this.categories_obj.querySelectorAll("button");
                    if (buttons.length > 0)
                    {
                        var selected_i = null;
                        buttons.forEach((elem, i) => {
                            if (elem.classList.contains("selected"))
                                selected_i = i;
                        });
                        if (selected_i !== null)
                            this.move_category(buttons[selected_i].id.replace("category_", ""));
                    }
                }
                if (e.keyCode === 38 || e.keyCode === 40) this.navigate_categories(e.keyCode);
            }
        });
        this.input_obj.addEventListener("input", ()=>this.show_categories());
        this.categories_obj = $target.querySelector("div.categories");
        this.categories_obj.addEventListener("click", (e) => {
            if (e.target.nodeName === "BUTTON")
                this.move_category(e.target.id.replace("category_", ""));
        });
        this.categories_hide();
        this.categories = [];
        this.get_categories();
    }

    clear_input()
    {
        this.input_obj.value = '';
        this.add_button_hide();
    }

    navigate_categories(key)
    {
        const buttons = this.categories_obj.querySelectorAll("button");
        if (buttons.length > 0)
        {
            var selected_i = null;
            buttons.forEach((elem, i) => {
                if (elem.classList.contains("selected"))
                    selected_i = i;
            });
            if (selected_i !== null)
            {
                if ((selected_i === 0 && key === 38) || (selected_i === buttons.length-1 && key === 40) )
                {
                }
                else
                {
                    buttons[selected_i].classList.remove("selected");
                    if (buttons[selected_i + (key===38 ? -1 : 1)].classList.contains("selected") === false)
                        buttons[selected_i + (key===38 ? -1 : 1)].classList.add("selected");
                }
            }
            else if (buttons[0].classList.contains("selected") === false) buttons[0].classList.add("selected");
        }
    }

    get_categories()
    {
        api.get({mode:"fetch_categories"})
        .then(response => {
            if (response.ok) return response.json();
            throw new Error("Request failed. Try again.");
        }).then(response=>{
            this.categories = response;
            const allCategory = this.categories.find(category => category.name === "All");
            if (allCategory) {
                localStorage.setItem('content_category_id', allCategory.id);
                document.querySelector("iframe").src = "/components/content.html";
            }
            const noneCategory = this.categories.find(category => category.name === "None");
            if (noneCategory) {
                user_none_category_id = noneCategory.id;
            }
        }).catch(error=>{
            alert(error);
        });
    }

    add_button_hide() //처음 로드됐을 때, 카테고리 추가에 성공했을 때 실행됨. 
    {
        if (this.add_button_obj.classList.contains("hide") === false)
            this.add_button_obj.classList.add("hide");
    }

    add_category()
    {
        api.get({mode:"update_category", name:encodeURIComponent(this.input_obj.value)})
        .then(response => {
            if (response.ok) return response.json();
            throw new Error("Request failed. Try again.");
        }).then(id=>{
            this.add_button_hide();
            this.move_category(id);
        }).catch(error=>{
            alert(error);
        });
    }

    move_category(category_id)
    {
        localStorage.setItem('content_category_id', category_id);
        document.querySelector("iframe").src = "/components/content.html"; 
    }

    categories_stretch()
    {
        const buttons = this.categories_obj.querySelectorAll("button");
        if (buttons.length > 0)
        {
            const new_height = (buttons[0].offsetHeight + 10) * buttons.length;
            this.categories_obj.style.bottom = `-${new_height}px`;
            this.categories_obj.style.height = new_height + 'px';
        }
        else
            this.add_button_obj.classList.remove("hide");
    }

    categories_shorten()
    {
        this.add_button_hide();
        this.categories_obj.innerHTML = '';
        this.categories_obj.style.bottom = `0px`;
        this.categories_obj.style.height = '0px';
    }

    show_categories()
    {
        this.categories_shorten();
        this.categories_obj.classList.remove("hide");
        this.categories.forEach(elem => {
            const search_str = this.input_obj.value;
            if (elem['name'].substr(0, search_str.length).toLowerCase() === search_str.toLowerCase() || search_str === "")
            {
                const button_obj = document.createElement("button"), replaced = elem['name'].toLowerCase().replace(search_str, "");
                button_obj.classList.add("categories");
                button_obj.innerHTML = `<span style='font-weight:bold'>${search_str}</span>${elem['name'].substr(search_str.length, elem['name'].length)}`;
                button_obj.id = `category_${elem['id']}`;
                this.categories_obj.appendChild(button_obj);
                if (elem['name'].toLowerCase() === search_str.toLowerCase())
                    button_obj.classList.add("selected");
            }
        });
        this.categories_stretch();
    }

    categories_hide()
    {
        if (this.categories_obj.classList.contains("hide") === false)
            this.categories_obj.classList.add("hide");
    }

        // 카테고리 네비게이션을 하는 객체.
        // 이 안에는 input 박스가 있고, 여기다 카테고리 제목을 치면 자동으로 이동할 카테고리를 추천. 
        // All 카테고리 버튼이 있음. 
        // 참고로 메시지 작성 시엔 카테고리 설정 못하고 무조건 all로 올라감. 작성된 메시지 클릭 시 카테고리 이동 윈도우 띄움.
        // 메시지 옆에는 작성시간, 네비게이션 버튼이 있음.
        // 메시지 살짝 터치하면 카테고리 수정 모드. 길게 터치하면 내용 수정모드.
        // 삭제는 delete 카테고리로 이동.
}



/*

와 의외로 효율적인 컨텐트 구성 방법이 잘 안 떠오르네....

1. fetch로 메시지 데이터를 db에서 가져온다.

2. content_obj에는 이미 render된 메시지 div들이 잔뜩 있다.

3. fetch로 가져온 메시지 데이터는 이번에 send로 새로 추가된 div일 수도 있고, 무한 스크롤로 새로 가져온 div일 수도 있다.
- 새로 추가된 div는 appendChild로 추가하면 됨.
- 무한 스크롤로 새로 가져온 div는 insertBefore로 추가해야 함.


*/



/*


구현해야 하는 거 목록


1. message div 안에 화살표 버튼 추가 및 관련 이벤트리스너 추가
- 화살표 버튼은 필수. 강력한 메시지 타래 구성 및 관리 기능 지원이 핵심 아이덴티티이기 때문에.

2. message div끼리 계층 구조 만들어 보여서 렌더링
- 이거 생각해봤는데 indentation을 db에 기록하는 게 최선 같음... insertBefore 하면서 인덴테이션 개수만큼 옆으로 옮기는...
- '부모를 기록한다'라고 하면... insertBefore로 구현하는 특성상 인덴테이션 몇개나 넣어야 하는지 부모까지 타고 올라가는.. 그런 복잡한 낭비가 필요.. 그런거 너무 낭비.

3. 메시지 잘라내기, 삽입하기, 댓글달기 기능을 만들어야.
- 이거 하려면 메시지 idx 테이블 없애고 메시지 위아래 리스트 구조로 구현해야. 
- 굉장히 구현이 복잡해지지만 메시지 타래 구성이 컨셉이라면 필수라고 생각됨.

4. 메시지 살짝 터치 시 카테고리 수정
- 메시지 하나 카테고리 옮길 때 위아래 타래 같이 옮겨야.

5. 길게 터치 시 내용 수정

6. 모든 div들 css...


7. 텍스트 드래그용으로 날짜, 버튼 가리는 버튼 기능을 추가할까... 있으면 좋긴 할텐데 날짜 정도는 있는 게 낫나. 일단 완성해보고 고민.





디비 API 만들고 다한거 아닌가 싶었는데 ㅡㅡ; 이제 겨우 반 한 거인.... 시바 졸려 죽겠는데 ㅠㅠ

내일 저녁에 조금이라도 구현 진도 나갈 수 있을까... 생각보다 구현이 엄청 복잡해서 살짝 번아웃... 주말에 잠도 너무 못잤고..

해야할거 하나도 못했고 ㅠㅠ

일단 오늘은 이쯤 하고 자고 주중에 뭘 시도를 해보든지 아니면 다음 주말이나 그 이후로 미루든지.... 해볼건 많겠지



*/



class Textarea {
    constructor($target)
    {
        this.$target = $target;
        this.textarea_obj = $target.querySelector("textarea");
        this.button_obj = $target.querySelector("button");
        this.textarea_obj.addEventListener("input", ()=>this.reset_textarea_height());
        this.button_obj.addEventListener("click", (e)=> { if (this.textarea_obj.value !== "") 
        {
            this.textarea_obj.focus();
            this.send(); 
        }});
        
        this.textarea_obj.focus();
    }

    reset_textarea_height()
    {
        if (this.textarea_obj.scrollHeight < window.innerHeight / 2)
        {
            this.textarea_obj.style.height = this.textarea_obj.value === "" ? "50px" : this.textarea_obj.scrollHeight + 'px';
            this.$target.style.height = this.textarea_obj.value === "" ? "60px" : this.textarea_obj.scrollHeight + 10 + 'px';
        }
        this.button_obj.style.height = this.textarea_obj.style.height;
        document.documentElement.style.setProperty('--input-height', this.textarea_obj.clientHeight+'px');        
    }

    send()
    {
        var temp = this.textarea_obj.value;
        this.textarea_obj.value = "";
        this.reset_textarea_height();

        api.get({mode:"write_message", message:encodeURIComponent(temp), written_date:Date.now(), category_id: user_none_category_id})
        .then(response => {
            if (response.ok)
            {
                document.querySelector("iframe").src = "/components/content.html";
                return;
            }
            throw new Error("Request failed. Try again.");
        }).catch(error=>{
            this.textarea_obj.value = temp;
            alert(error);
        });
    }
}

let user_none_category_id;
window.onload = async ()=>{
    new Title(document.querySelector("main > div.title"));
    new Textarea(document.querySelector("main > div.textarea"));
    fetch('/api/profile?property=name')
    .then(response => response.json())
    .then(data => {
        if (data.value) {
            document.getElementById('username').innerText = `Hello, ${data.value}!`;
        }
    });
}
