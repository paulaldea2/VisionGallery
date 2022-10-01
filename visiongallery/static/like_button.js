import React, { Component } from 'react';
'use strict';

const e = React.createElement;

class LikeButton extends React.Component {
    render() {
        return (
                <div class="container py-5" >
                    <div class="row d-flex justify-content-center align-items-center" style="margin-left:35%; margin-right:35%;">
                            <div class="card shadow-2-strong" style="border-radius: 1rem;">
                                <div class="card-body p-5">
                                    <h3 class="text-center"> Log In here </h3>
                                    <p>{{ error_message }}</p>
                                    {/* <form method="get" >
                                        <div class="form-outline mb-4">
                                        {% csrf_token %}
                                        {{ login }}
                                        </div>
                                        <div class="text-center">
                                        <a href="/recover_account/step_1">Forget Your Password?</a><br><br>
                                        <button class="btn btn-primary" type="submit">Login</button>
                                        </div>
                                    </form> */}
                                </div>
                            </div>
                        </div>
                    </div>
        );
    }
    // constructor(props) {
    // super(props);
    // this.state = { liked: false };
    // } 

    // render() {
    //     if (this.state.liked) {
    //     return 'You liked this.';
    //     }

    //     return e(
    //     'button',
    //     { onClick: () => this.setState({ liked: true }) },
    //     'Like'
    //     );
    // }
}

const domContainer = document.querySelector('#like_button_container');
const root = ReactDOM.createRoot(domContainer);
root.render(e(LikeButton));