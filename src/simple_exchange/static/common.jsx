class StockAddForm extends React.Component {
	constructor(props){
		super(props);
		this.state = {nameEntry: '', pxEntry:'', disabled: false, tick: '10'};
	}
	submit(e) {
		e.preventDefault();
		$.ajax({
			type: "POST",
			contentType: 'application/json',
			url: 'stock/' + this.state.nameEntry,
			data: JSON.stringify({name: this.state.nameEntry, initpx: this.state.pxEntry, tick:this.state.tick}),
			success: this.success.bind(this),
			dataType: 'json',
		});
	}
	success() {
		window.location.reload();
	}
	nameChanged(event) {
		var val = event.target.value;
		this.setState((prevState, props)=>{return {nameEntry: val}});
	}
	tickChanged(event) {
		var val = event.target.value;
		this.setState((prevState, props)=>{return {tick: val}});
	}
	initPriceChanged(event) {
		var val = event.target.value;
		this.setState((prevState, props)=>{return {pxEntry: val}});
	}
	render() {
		return <form onSubmit={this.submit.bind(this)}>
			Add stock: <input type="text" onChange={this.nameChanged.bind(this)} value={this.state.nameEntry}/>
			Initial px: <input type="text" onChange={this.initPriceChanged.bind(this)} value={this.state.pxEntry}/>
			Tick size: <input type="text" onChange={this.tickChanged.bind(this)} value={this.state.tick}/>
			<input type="submit" onClick={this.submit.bind(this)} disabled={this.state.disabled} />
		</form>
	}
}

class StocksList extends React.Component {
	constructor(props){
		super(props);
		this.state = { list: []};
		this.refresh.bind(this)();
	}
	refresh() {
		$.ajax({type: 'GET', url: 'stocks', success: this.success.bind(this)});
	}
	success(data) {
		this.setState((prevState, props) => {
			return { list: data };
		});
	}
	render() {
		return <div>{this.state.list.map((x)=>(<Stock data={x}/>))}</div>;
	}
}

class Stock extends React.Component {
	constructor(props) {
		super(props);
		this.state = {pxEntry: this.props.data.px, disabled: false, tick: this.props.data.tick || '10'}
	}
	submit(e) {
		e.preventDefault();
		$.ajax({
			type: "PUT",
			contentType: 'application/json',
			url: 'stock/' + this.props.data.name,
			data: JSON.stringify({name: this.props.data.name, initpx: this.state.pxEntry, tick:this.state.tick}),
			success: this.success.bind(this),
			dataType: 'json',
		});
	}
	success() {
		window.location.reload();
	}
	tickChanged(event) {
		var val = event.target.value;
		this.setState((prevState, props)=>{return {tick: val}});
	}
	priceChanged(event) {
		var val = event.target.value;
		this.setState((prevState, props)=>{return {pxEntry: val}});
	}
	can/*cel*/(e) {
		e.preventDefault();
		$.ajax({
			type: "DELETE",
			url: 'stock/' + this.props.data.name,
			success: this.success.bind(this),
			dataType: 'json',
		});
	}
	render() {
		return <form onSubmit={this.submit.bind(this)}>
					Stock: {this.props.data.name} Px: <input type="text" onChange={this.priceChanged.bind(this)} value={this.state.pxEntry}/> Tick: <input type="text" onChange={this.tickChanged.bind(this)} value={this.state.tick} />
					<input type="submit" onClick={this.submit.bind(this)} disabled={this.state.disabled} />
					<button onClick={this.can.bind(this)}>Delete</button>
		</form>;
	}
}
