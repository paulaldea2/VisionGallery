import React, {useState} from 'react'
import './login.scss';
import {Button} from 'antd';
import {useHistory} from 'react-router-dom'

export default function Login() {
    // 声明一个新的叫做 “count” 的 state 变量
    const [count, setCount] = useState(0)
    const history = useHistory()
    return (
        <div className='login flex-col--c'>
            <header className='flex-row-c-c'>
                <div className='header-box flex-row-sb-c'>
                    <img src="/static/logo.jpg" alt=""/>
                    <Button type="primary" className="mt10" onClick={() => {
                        history.push({pathname: '/register'})
                    }}>Register</Button>
                </div>
            </header>
            <div className='center-box'>
                <div className="content-box flex-row-sb-c">
                    <div className="form-box flex-col">
                        <p className='p-1'>Sign in</p>
                        <p className='p-2'>Enter your details below</p>
                        <input type="text" placeholder='email' className="email"/>
                        <input type="text" placeholder='password' className="pass mt10"/>
                        <Button size='large' type="primary" className="mt10">Login</Button>
                        <span className='go-to' onClick={() => {
                            history.push({pathname: '/register'})
                        }}>Click here to <span className='_'>Register</span></span>
                    </div>
                    <img className='right-img' src="/static/img-1.jpg" alt=""/>
                </div>
            </div>

            <div className="footer flex-col-c-c">
                <img src="/static/logo.jpg" alt=""/>
                <p>Copyright © 2022 Vision Gallery. Inc.</p>
            </div>
        </div>
    )
}
