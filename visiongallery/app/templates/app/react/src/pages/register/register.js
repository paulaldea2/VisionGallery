import React, { useState } from 'react'
import { useHistory } from 'react-router-dom'
import './register.scss'
import { Button, Checkbox } from 'antd'

export default function Register() {
  // 声明一个新的叫做 “count” 的 state 变量
  // const [count, setCount] = useState(0)
  const history = useHistory()
  const onChange = () => {}
  return (
    <div className="register flex-col--c">
      <header className="flex-row-c-c">
        <div className="header-box flex-row-sb-c">
          <img src="/static/logo.jpg" alt="" />
          <Button
            type="primary"
            className="mt10"
            onClick={() => {
              history.push({ pathname: '/login' })
            }}
          >
            Login
          </Button>
        </div>
      </header>
      <div className="center-box">
        <div className="content-box flex-row-sb-c">
          <div className="form-box flex-col">
            <p className="p-1">Register</p>
            <p className="p-2">Enter your details below</p>
            <input type="text" placeholder="email" />
            <input type="text" placeholder="Username" className=" mt10" />
            <input type="text" placeholder="password" className=" mt10" />
            <input type="text" placeholder="Confirm password" className=" mt10" />
            <Button size="large" type="primary" className="mt10">
              Register
            </Button>
            <p style={{ marginTop: '10px' }}>
              <Checkbox onChange={onChange}>
                I agree with{' '}
                <a
                  onClick={() => {
                    history.push({ pathname: '/privacy' })
                  }}
                >
                  GDPR policy
                </a>{' '}
              </Checkbox>
            </p>
            <span
              className="go-to"
              onClick={() => {
                history.push({ pathname: '/login' })
              }}
            >
              Click here to <span className="_">Login</span>
            </span>
          </div>
          <img className="right-img" src="/static/img-1.jpg" alt="" />
        </div>
      </div>

      <div className="footer flex-col-c-c">
        <img src="/static/logo.jpg" alt="" />
        <p>Copyright © 2022 Vision Gallery. Inc.</p>
      </div>
    </div>
  )
}
