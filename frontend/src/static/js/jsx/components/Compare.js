import React from 'react';
import apiRequest from '../utils/jobsSDK';
import Checkbox from 'material-ui/Checkbox';
import VerticalView from './VerticalView';
import Grid from 'material-ui/Grid';
import List, {ListItem, ListItemSecondaryAction, ListItemText} from 'material-ui/List';

const styles = {
  compare: {
    display: 'flex',
    flexDirection: 'row',
  },
};

class Compare extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      companies: [],
      appIds: [],
      checkedValues: [],
    };

    var self = this;
    apiRequest('applications', function(body) {
      self.setState({
        companies: body.map(function(company) {
          return [company.appId, company.company];
        }),
      });
    });

    this.handleCheck = this.handleCheck.bind(this);
  }

  handleCheck(appId) {
    const found = this.state.checkedValues.includes(appId);
    if (found) {
      this.setState({
        checkedValues: this.state.checkedValues.filter(x => x !== appId),
      });
    } else {
      this.setState({
        checkedValues: [...this.state.checkedValues, appId],
      });
    }
  }

  render() {
    return (
      <div>
        <Grid container={true} spacing={16} direction='row' alignItems='flex-start' justify='flex-start'>
          <Grid item={true} md={true} style={{flexGrow: 0}}>
        <List>
        {
          this.state.companies.map((company) => {
            return (
              <ListItem
                key={company[0]}
                role={undefined}
                dense={true}
                button={true}
                onClick={() => this.handleCheck(company[0])}
                style={{padding: 0}}
              >
              <Checkbox
                checked={this.state.checkedValues.includes(company[0])}
              />
              <ListItemText primary={company[1]}/>
            </ListItem>
            );
          })
        }
      </List>
    </Grid>

    <Grid item={true} md={true} style={{flexGrow: 0}}>
            <VerticalView appId={this.state.checkedValues}/>
          </Grid>
        </Grid>
      </div>
    );
  }
}

export default Compare;
