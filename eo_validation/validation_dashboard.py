import os
import pwd
import copy
import math
import time
import socket
import ipysheet
import ipyleaflet
import numpy as np
import pandas as pd
import geopandas as gpd
import rioxarray as rxr
import ipywidgets as widgets

try:
    import whiteboxgui.whiteboxgui as wbt
    whitebox_imported = True
except FileNotFoundError:
    whitebox_imported = False


from glob import glob
from pathlib import Path
from ipyfilechooser import FileChooser
from IPython.display import display
from ipyleaflet import (
    FullScreenControl,
    LayersControl,
    DrawControl,
    MeasureControl,
    ScaleControl,
    Marker,
    basemaps,
    AwesomeIcon,
    MarkerCluster,
    WidgetControl,
    GeoData,
    TileLayer,
    Popup
)
from shapely.geometry import shape
from eo_validation.async_write import AsyncWriteGDF


if os.getenv("JUPYTERHUB_SERVICE_PREFIX") is not None:
    os.environ['LOCALTILESERVER_CLIENT_PREFIX'] = \
        f"{os.environ['JUPYTERHUB_SERVICE_PREFIX'].lstrip('/')}/proxy/{{port}}"

from localtileserver import get_leaflet_tile_layer, TileClient


class ValidationDashboard(ipyleaflet.Map):
    """This Map class inherits the ipyleaflet Map class.
    Modified: https://github.com/giswqs/geodemo/blob/master/geodemo/geodemo.py
    Args:
        ipyleaflet (ipyleaflet.Map): An ipyleaflet map.
        center (list int): location to center the map
    Returns:
        object: ipyleaflet map object.
    """

    def __init__(self, **kwargs):

        # Define center start
        if "center" not in kwargs:
            kwargs["center"] = [14, -14]

        # Define initial zoom level
        if "zoom" not in kwargs:
            kwargs["zoom"] = 6

        # Define max_zoom options
        if "max_zoom" not in kwargs:
            kwargs["max_zoom"] = 20
        else:
            self.mask_dir = kwargs["max_zoom"]

        # Define default_max_zoom options
        if "default_max_zoom" not in kwargs:
            self.default_max_zoom = 20
        else:
            self.default_max_zoom = kwargs["default_max_zoom"]

        # Define default_zoom options
        if "default_zoom" not in kwargs:
            self.default_zoom = 18
        else:
            self.default_zoom = kwargs["default_zoom"]

        # Define zoom capabilities
        if "scroll_wheel_zoom" not in kwargs:
            kwargs["scroll_wheel_zoom"] = True

        # Allow keyboard movements
        if "keyboard" not in kwargs:
            kwargs["keyboard"] = True

        # Define basemap options
        if "basemap" not in kwargs:
            kwargs["basemap"] = basemaps.Esri.WorldImagery

        super().__init__(**kwargs)

        # Define the height of the layout
        if "height" not in kwargs:
            self.layout.height = "600px"
        else:
            self.layout.height = kwargs["height"]

        # Add control widgets
        self.add_control(FullScreenControl())
        self.add_control(MeasureControl())
        self.add_control(LayersControl(position="topright"))
        self.add_control(DrawControl(position="topleft"))
        self.add_control(ScaleControl(position="bottomleft"))

        # Retrieve hostname
        self.hostname = socket.gethostname()

        # Retrieve username
        self.username = pwd.getpwuid(os.getuid())[0]

        # if the username is from a Daskhub instance with jovyan
        if self.username == 'jovyan':
            self.username = self.hostname.split('-')[-1]

        # Define data directory, if no argument given, proceed with defaults
        if "data_dir" not in kwargs:
            self.data_dir = os.path.expanduser('~')
        else:
            self.data_dir = kwargs['data_dir']
        assert os.path.exists(self.data_dir), f'{self.data_dir} does not exist'

        # Define labels directory, if no argument given, proceed with defaults
        if "mask_dir" not in kwargs:
            self.mask_dir = os.path.expanduser('~')
        else:
            self.mask_dir = kwargs['mask_dir']
        assert os.path.exists(self.mask_dir), f'{self.mask_dir} does not exist'

        # Define output directory, if no argument given, proceed with defaults
        if "output_dir" not in kwargs:
            self.output_dir = os.path.join(
                os.path.expanduser('~'), 'eo-validation-output'
            )
        else:
            self.output_dir = kwargs['output_dir']

        # Create output_dir
        self.output_dir = os.path.join(self.output_dir, self.username)
        os.makedirs(self.output_dir, exist_ok=True)

        # Cleanup data_dir and mask_dir variables
        self.data_dir = os.path.abspath(self.data_dir)
        self.mask_dir = os.path.abspath(self.mask_dir)

        # Define available raster bands
        if "default_bands" not in kwargs:
            self.default_bands = [
                ('Coastal Blue', 1), ('Blue', 2), ('Green', 3), ('Yellow', 4),
                ('Red', 5), ('Red Edge', 6), ('NIR1', 7), ('NIR2', 8)
            ]
        else:
            self.default_bands = kwargs['default_bands']

        # Define default RGB bands
        if "rgb_bands" not in kwargs:
            self.rgb_bands = [1, 2, 3]
        else:
            self.rgb_bands = kwargs['rgb_bands']
            assert len(self.rgb_bands) == 3, \
                f"rgb_bands expected 3 items, {len(self.rgb_bands)} given"

        # Define wether we allow users to define their own bands
        if "rgb_disabled" not in kwargs:
            self.rgb_disabled = False
        else:
            self.rgb_disabled = kwargs['rgb_disabled']

        # Define validation classes
        if "validation_classes" not in kwargs:
            self.validation_classes = [
                'other', 'trees/shrub', 'cropland', 'other vegetation',
                'water', 'build'
            ]
        else:
            self.validation_classes = kwargs['validation_classes']

        # Define mask classes
        if "mask_classes" not in kwargs:
            self.mask_classes = ['other', 'tree', 'crop', 'burn']
        else:
            self.mask_classes = kwargs['mask_classes']

        # Define default mask classes
        if "default_class" not in kwargs:
            self.default_class = self.validation_classes[0]
        else:
            self.default_class = kwargs['default_class']

        # Define pre-generated validations points
        if "points_dir" not in kwargs:
            self.points_dir = os.path.join(
                os.path.expanduser('~'), 'eo-validation', 'original_points'
            )
        else:
            self.points_dir = kwargs['points_dir']

        # Define if validation points need to be generated
        if "gen_points" not in kwargs:
            self.gen_points = True
        else:
            self.gen_points = kwargs['gen_points']

        # Define if we have a validation database given
        # Here we are basically overriding the gen_points option if we already
        # have some of the data, the classes are part of this process as well
        if "validation_points_filename" not in kwargs:
            self.validation_points_filename = None
        else:
            self.validation_points_filename = \
                kwargs['validation_points_filename']
            self.gen_points = False

        # TODO: split points by column
        if "filter_points_by" not in kwargs:
            self.filter_points_by = None
        else:
            self.filter_points_by = kwargs['filter_points_by']

        # polygon or point for the marker
        if "marker_type" not in kwargs:
            self.marker_type = 'point'
        else:
            self.marker_type = kwargs['marker_type']

        # Define if validation points need to be generated
        if "n_points" not in kwargs:
            self.n_points = 200
        else:
            self.n_points = kwargs['n_points']

        if "expected_accuracies" not in kwargs:
            self.expected_accuracies = [0.90, 0.90, 0.90, 0.90]
        else:
            self.expected_accuracies = kwargs['expected_accuracies']

        if "expected_standard_error" not in kwargs:
            self.expected_standard_error = 0.01
        else:
            self.expected_standard_error = kwargs['expected_standard_error']

        # Set xarray chunk attributes
        if "chunks" not in kwargs:
            self.chunks = {"band": 1, "x": 2048, "y": 2048}
        else:
            self.chunks = kwargs["chunks"]

        self.output_filename = None
        self.raster_crs = None

        self._validation_sheet = None
        self._markers_dict = dict()
        self._marker_counter = -1

        self._current_marker_id = None
        self._current_time = None
        self._seconds_per_point = None

        self.async_writer = AsyncWriteGDF()

        # Adding default Google Basemap
        google_satellite_basemap = TileLayer(
            url='https://mt0.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            name='Google Satellite', max_zoom=80)
        self.add_layer(google_satellite_basemap)

        # Start main toolbar
        self._main_toolbar()

    def add_raster(
            self,
            in_raster: str,
            data_bands: list = [5, 7, 2],
            cmap: list = None,
            sigma: int = 2,
            layer_name: str = "Raster") -> None:
        """
        Adds a raster layer to the map.
        """
        # create TileClient object
        raster_client = TileClient(in_raster)

        style_list = []
        for bid, pid in zip(data_bands, ['#f00', '#0f0', '#00f']):
            band_stats = raster_client.rasterio.statistics(bid)
            newmin = band_stats.mean - (band_stats.std * sigma)
            newmax = band_stats.mean + (band_stats.std * sigma)
            style_list.append(
                {'band': bid, 'palette': pid, 'min': newmin, 'max': newmax})

        self.add_layer(
            get_leaflet_tile_layer(
                raster_client, show=False, band=data_bands,
                cmap=cmap, max_zoom=self.default_max_zoom,
                max_native_zoom=self.default_max_zoom,
                name=layer_name, scheme='linear',
                dtype='uint16', style={'bands': style_list}
            )
        )
        self.center = raster_client.center()  # center Map around raster
        self.zoom = raster_client.default_zoom  # zoom to raster center

    def generate_points(
                self,
                raster_filename: str,
                mask_filename: str,
                n_points: int = None
            ):
        """
        Generate points.
        """
        if mask_filename is not None:

            # read prediction raster
            raster_prediction = rxr.open_rasterio(
                mask_filename, chunks=self.chunks)
            raster_prediction.name = "predicted"
            raster_prediction = raster_prediction.rio.reproject("EPSG:4326")
            self.raster_crs = raster_prediction.rio.crs

            # Convert to dataframe and filter no-data
            raster_prediction = \
                raster_prediction.squeeze().to_dataframe().reset_index()

            # drop some unecessary columns
            raster_prediction = raster_prediction.drop(
                ['band', 'spatial_ref'], axis=1)

            # Only select appropiate values, remove no-data
            raster_prediction = raster_prediction[
                raster_prediction['predicted'] >= 0]
            raster_prediction = raster_prediction[
                raster_prediction['predicted'] < 255]

            # Make sure classes start from 1, substract 1 if not
            if raster_prediction['predicted'].min() > 0:
                raster_prediction['predicted'] = \
                    raster_prediction['predicted'] - 1

            # Convert mask to int
            raster_prediction = raster_prediction.astype({'predicted': 'int'})
            unique_counts = raster_prediction['predicted'].value_counts()
            original_shape = raster_prediction.shape[0]

            # Make sure expected accuracies match size of classes found
            if len(self.expected_accuracies) != \
                    raster_prediction['predicted'].max() + 1:
                self.expected_accuracies = \
                    [self.expected_accuracies[0]] * \
                    (raster_prediction['predicted'].max() + 1)

            percentage_counts, standard_deviation = [], []
            for class_id, class_count in unique_counts.iteritems():
                percentage_counts.append(class_count / original_shape)
                standard_deviation.append(
                    math.sqrt(
                        self.expected_accuracies[class_id]
                        * (1 - self.expected_accuracies[class_id]))
                )

            unique_counts = unique_counts.to_frame()
            unique_counts['percent'] = percentage_counts
            unique_counts['standard_deviation'] = standard_deviation
            unique_counts = unique_counts.round(2)

            # Choose between Oloffson or static number of points
            if n_points is not None:
                val_total_points = n_points
            else:
                val_total_points = round(((
                    unique_counts['percent']
                    * unique_counts['standard_deviation']).sum()
                    / self.expected_standard_error) ** 2)

            # Get the number of points per class
            unique_counts['n_point'] = \
                (unique_counts['percent'] * val_total_points).apply(np.floor)

            if unique_counts['n_point'].sum() < val_total_points:
                unique_counts.at[0, 'n_point'] += \
                    val_total_points - unique_counts['n_point'].sum()
            elif unique_counts['n_point'].sum() > val_total_points:
                unique_counts.at[
                    unique_counts['n_point'].idxmax(), 'n_point'] -= \
                    unique_counts['n_point'].sum() - val_total_points

            for class_id, row in unique_counts.iterrows():
                raster_prediction = raster_prediction.drop(
                    raster_prediction[
                        raster_prediction['predicted'] == class_id].sample(
                            n=int(row['predicted'] - row['n_point']),
                            random_state=24).index
                )

        # we do not have any mask filename
        else:

            # read prediction raster
            raster_prediction = rxr.open_rasterio(
                raster_filename, chunks=self.chunks)[0, :, :]
            raster_prediction.name = "predicted"
            raster_prediction = raster_prediction.rio.reproject("EPSG:4326")
            self.raster_crs = raster_prediction.rio.crs

            # Convert to dataframe and filter no-data
            raster_prediction = \
                raster_prediction.squeeze().to_dataframe().reset_index()

            # drop some unecessary columns
            raster_prediction = raster_prediction.drop(
                ['band', 'spatial_ref'], axis=1)

            # Only select appropiate values, remove no-data
            raster_prediction = raster_prediction[
                raster_prediction['predicted'] >= 0]

            # Convert mask to int
            raster_prediction = raster_prediction.astype({'predicted': 'int'})

            # Generate random points (drop randomly from the dataset
            raster_prediction = raster_prediction.sample(n=n_points)

        # Generate geometry dataframe
        geometry = gpd.points_from_xy(raster_prediction.x, raster_prediction.y)
        raster_prediction = gpd.GeoDataFrame(
            raster_prediction,
            crs=self.raster_crs,
            geometry=geometry).reset_index(drop=True)

        return raster_prediction

    def calculate_centroid(self, polygon_coordinates, geom_type):
        polygon = shape({
            "type": geom_type,
            "coordinates": polygon_coordinates
        })
        centroid = polygon.centroid
        return centroid.y, centroid.x  # Return as (lat, lon)

    def add_markers(
                self,
                in_raster: str,
                gen_points: bool = True,
                n_points: int = None,
                offline: bool = False
            ):

        # Extract label filename from data filename
        mask_filename = glob(
            os.path.join(self.mask_dir, f'{Path(in_raster).stem}*.tif'))

        if len(mask_filename) > 0:
            mask_filename = mask_filename[0]
        else:
            mask_filename = None

        original_points_filename = os.path.join(
            self.points_dir, f'{Path(in_raster).stem}.gpkg')

        # Extract output filename if None available and doing offline points
        if self.output_filename is None or offline:
            self.output_filename = os.path.join(
                self.output_dir, f"{Path(in_raster).stem}.gpkg")

        # Case #1: student is already working on the points
        if not gen_points or os.path.isfile(self.output_filename):
            validation_points = self.load_gpkg(self.output_filename)
            validation_points = validation_points.to_crs(epsg=4326)

        # Case #2: points have already been generated for everyone
        elif not gen_points or os.path.isfile(original_points_filename):
            validation_points = self.load_gpkg(original_points_filename)
            validation_points = validation_points.to_crs(epsg=4326)

        # Case #3: no points available, generate them from scratch
        else:
            validation_points = self.generate_points(
                in_raster, mask_filename, n_points)
            validation_points = validation_points.drop(
                ['predicted'], axis=1).to_crs(4326)
            validation_points['operator'] = self.default_class
            validation_points['burnt'] = 0
            validation_points['confidence'] = 1
            validation_points['verified'] = 'false'
            validation_points['date'] = None
            validation_points['seconds_taken'] = None

        # Create ipysheet object
        self._validation_sheet = ipysheet.sheet(
            ipysheet.from_dataframe(
                validation_points.to_crs(4326).drop(['geometry'], axis=1)))
        widgets.Dropdown.value.tag(sync=True)

        if not offline:

            # Iterate over each point and add them to the map
            for index, point in validation_points.iterrows():

                # get coordinates
                coordinates = (point['geometry'].y, point['geometry'].x)
                if point['verified'] == 'false' or not point['verified']:
                    verified_option = False
                else:
                    verified_option = True

                radio_check_widget = widgets.RadioButtons(
                    options=self.validation_classes,
                    value=point['operator'],
                    layout={'width': 'max-content'},
                    description='Validation:',
                    disabled=False
                )

                radio_burn_widget = widgets.RadioButtons(
                    options=[('not-burnt', 0), ('burnt', 1)],
                    value=point['burnt'],
                    layout={'width': 'max-content'},
                    description='Burnt:',
                    disabled=False
                )

                radio_confidence_widget = widgets.RadioButtons(
                    options=[
                        ('high-confidence', 1),
                        ('medium-confidence', 2),
                        ('low-confidence', 3)],
                    value=point['confidence'],
                    layout={'width': 'max-content'},
                    description='Confidence:',
                    disabled=False
                )

                point_id_widget = widgets.IntText(
                    value=index,
                    description='ID:',
                    disabled=True
                )

                checked_widget = widgets.Checkbox(
                    value=verified_option,
                    description='Verified:',
                    disabled=False
                )

                popup = widgets.VBox([
                    point_id_widget,
                    radio_check_widget,
                    radio_burn_widget,
                    radio_confidence_widget,
                    checked_widget
                ])

                marker = Marker(
                    name=str(index),
                    location=coordinates,
                    draggable=False,
                    keyboard=True,
                    popup=popup
                )

                if verified_option:
                    marker.icon = AwesomeIcon(
                        name='check-square',
                        marker_color='green',
                        icon_color='black'
                    )

                cell = ipysheet.cell(index, 2, point['operator'])
                widgets.jslink((cell, 'value'), (radio_check_widget, 'value'))
                cell = ipysheet.cell(index, 3, point['burnt'])
                widgets.jslink((cell, 'value'), (radio_burn_widget, 'value'))
                cell = ipysheet.cell(index, 4, point['confidence'])
                widgets.jslink(
                    (cell, 'value'), (radio_confidence_widget, 'value'))
                cell = ipysheet.cell(index, 5, verified_option)
                widgets.jslink((cell, 'value'), (checked_widget, 'value'))

                # Store the real marker object in the dictionary
                self._markers_dict[tuple(marker.location)] = marker

                def handle_marker_on_click(*args, **kwargs):

                    self._markers_dict[
                        tuple(kwargs['coordinates'])].icon = AwesomeIcon(
                            name='check-square',
                            marker_color='green',
                            icon_color='black'
                    )

                    self.save_gpkg(
                        ipysheet.to_dataframe(self._validation_sheet),
                        self.output_filename
                    )
                marker.on_click(handle_marker_on_click)

            marker_cluster = MarkerCluster(
                markers=tuple(list(self._markers_dict.values())),
                name="validation"
            )

            # Add layer to map
            self.add_layer(marker_cluster)

        # Save GPKG file with dataframe
        self.save_gpkg(
            ipysheet.to_dataframe(self._validation_sheet),
            self.output_filename
        )

        return

    def add_polygon_markers(
                self,
                in_filename: str
            ):

        # Extract output filename if None available and doing offline points
        if self.output_filename is None:
            # self.output_filename = os.path.join(
            #    self.output_dir, f"{Path(in_filename).stem}.gpkg")
            self.output_filename = os.path.join(
                self.output_dir, f"{Path(in_filename).stem}.gpkg")

        # Case #1: student is already working on the points
        if os.path.isfile(self.output_filename):
            validation_points = self.load_gpkg(self.output_filename)
            validation_points = validation_points.to_crs(epsg=4326)

        # Case #2: points have already been generated for everyone
        elif os.path.isfile(in_filename):

            validation_points = self.load_gpkg(in_filename)
            validation_points = validation_points.to_crs(epsg=4326)

            validation_points['operator'] = self.default_class
            validation_points['burnt'] = 0
            validation_points['confidence'] = 1
            validation_points['verified'] = False  # 'false'
            validation_points['date'] = None
            validation_points['seconds_taken'] = None

        # Create ipysheet object
        self._validation_sheet = ipysheet.sheet(
            ipysheet.from_dataframe(
                validation_points.to_crs(4326).drop(['geometry'], axis=1)))
        widgets.Dropdown.value.tag(sync=True)

        # Adding geodatalayer
        self.geo_data_layer = GeoData(
            geo_dataframe=validation_points,
            style={'color': 'black', 'fillColor': 'red'},
            hover_style={'fillColor': 'white', 'fillOpacity': 0},
            name='Validation'
        )

        if self.filter_points_by is not None:
            validation_points = validation_points[
                validation_points['Group'] == self.filter_points_by]

        self._markers_dict = dict.fromkeys(
            list(zip(validation_points.y.astype(float),
                     validation_points.x.astype(float))),
            validation_points.Group
        )

        self.geo_data_layer.on_click(self.on_click_polygon_object)
        self.add_layer(self.geo_data_layer)
        self._geo_data = self.geo_data_layer.data

        return

    def create_property_widgets(self, properties):
        """Dynamically create widgets for each property."""

        # get property items for each marker
        property_items = dict(properties.items())

        # adding all properties
        if property_items['verified'] == 'false' \
                or not property_items['verified']:
            verified_option = False
        else:
            verified_option = True

        radio_check_widget = widgets.RadioButtons(
            options=self.validation_classes,
            value=property_items['operator'],
            layout={'width': 'max-content'},
            description='Validation:',
            disabled=False
        )
        radio_check_widget._property_key = 'operator'

        radio_burn_widget = widgets.RadioButtons(
            options=[('not-burnt', 0), ('burnt', 1)],
            value=property_items['burnt'],
            layout={'width': 'max-content'},
            description='Burnt:',
            disabled=False
        )
        radio_burn_widget._property_key = 'burnt'

        radio_confidence_widget = widgets.RadioButtons(
            options=[
                ('high-confidence', 1),
                ('medium-confidence', 2),
                ('low-confidence', 3)],
            value=property_items['confidence'],
            layout={'width': 'max-content'},
            description='Confidence:',
            disabled=False
        )
        radio_confidence_widget._property_key = 'confidence'

        point_id_widget = widgets.IntText(
            value=property_items['ID'],
            description='ID:',
            disabled=True
        )
        point_id_widget._property_key = 'ID'

        self._current_marker_id = property_items['ID']

        # (y, x) as (lat, lon)
        point_coords_widget_y = widgets.Text(
            value=str(property_items['y']),
            description='Lat:',
            disabled=True
        )
        point_coords_widget_y._property_key = 'y'

        point_coords_widget_x = widgets.Text(
            value=str(property_items['x']),
            description='Lon:',
            disabled=True
        )
        point_coords_widget_x._property_key = 'x'

        checked_widget = widgets.Checkbox(
            value=verified_option,
            description='Verified:',
            disabled=False
        )
        checked_widget._property_key = 'verified'

        def changed_checked_widget(b):

            # compute seconds per point taken
            self._seconds_per_point = round(
                    time.time() - self._current_time, 4)

            # update date of validated point
            self._feature['properties']['date'] = str(pd.Timestamp.now())

            # update seconds per point taken
            self._feature['properties']['seconds_taken'] = \
                self._seconds_per_point

            # Update the properties with the new values
            for widget in self.property_widgets:
                self._feature['properties'][widget._property_key] = \
                    widget.value

            # updating the information with new data
            self.geo_data_layer.geo_dataframe.loc[
                self.geo_data_layer.geo_dataframe['ID']
                == self._feature['properties']['ID'],
                self._feature['properties'].keys()] = \
                self._feature['properties'].values()

        checked_widget.observe(changed_checked_widget)

        popup = [
            point_id_widget,
            point_coords_widget_y,
            point_coords_widget_x,
            radio_check_widget,
            radio_burn_widget,
            radio_confidence_widget,
            checked_widget
        ]

        return popup

    def on_click_polygon_object(self, event, feature, **kwargs):

        # get current time
        self._current_time = time.time()
        self._feature = feature

        self._feature['properties'] = self.geo_data_layer.geo_dataframe.loc[
                self.geo_data_layer.geo_dataframe['ID']
                == self._feature['properties']['ID']
        ].to_dict(orient='records')[0]

        # Dynamically create input widgets for each property
        self.property_widgets = self.create_property_widgets(
            self._feature['properties'])

        save_button = widgets.Button(description="Save")
        geom_type = self._feature['geometry']['type']
        centroid = self.calculate_centroid(
            self._feature['geometry']['coordinates'], geom_type)

        box_layout = widgets.Layout(
            display='flex',
            flex_flow='column',
            align_items='center'
        )

        # Create and open the popup
        popup_content = widgets.VBox(
            self.property_widgets + [save_button], layout=box_layout)

        self._popup = Popup(
            location=centroid,
            child=popup_content,
            close_button=True,
            auto_close=False,
            close_on_escape_key=False,
            min_width=320,
            name='Observations'
        )

        self.add_layer(self._popup)

        def save_changes(_):

            original_data = copy.deepcopy(self.geo_data_layer.data)
            original_feature = copy.deepcopy(self._feature)

            # Update the properties with the new values
            for widget in self.property_widgets:
                self._feature['properties'][widget._property_key] = \
                    widget.value

            for i, f in enumerate(original_data['features']):
                if f == original_feature:
                    original_data['features'][i] = self._feature
                    break

            # Update the GeoJSON layer to reflect the changes
            self.geo_data_layer.data = original_data
            self._geo_data = original_data

            # updating the information with new data
            self.geo_data_layer.geo_dataframe.loc[
                self.geo_data_layer.geo_dataframe['ID']
                == self._feature['properties']['ID'],
                self._feature['properties'].keys()] = \
                self._feature['properties'].values()

            # saving output
            self.geo_data_layer.geo_dataframe.to_file(
                self.output_filename, layer='validation', driver="GPKG")

            # Close the popup by removing it from the map
            self.remove_layer(self._popup)

            self.center = tuple(
                list(self._markers_dict)[self._marker_counter])
            self.zoom = self.default_zoom

        # verified_widget.observe(save_changes)
        save_button.on_click(save_changes)

    def save_gpkg(self, df, output_filename, layer="validation"):
        """
        Save gpkg.
        """
        gdf = gpd.GeoDataFrame(
            df, crs=self.raster_crs,
            geometry=gpd.points_from_xy(df.x, df.y))
        gdf.to_file(output_filename, layer=layer, driver="GPKG")
        return

    def load_gpkg(self, input_filename):
        """
        Load gpkg.
        """
        # read file and drop index from dataframe
        gdf = gpd.read_file(input_filename).drop(
            ['index'], axis=1, errors='ignore')

        # save the raster/dataframe crs
        self.raster_crs = gdf.crs

        # check if the verified column exists, if not, create it
        if 'verified' not in gdf.columns:
            gdf['verified'] = False

        if self.filter_points_by is not None:
            verified_list = gdf[gdf['Group'] == self.filter_points_by][
                'verified'].tolist()
        else:
            verified_list = gdf['verified'].tolist()

        self._marker_counter = [
            i for i, x in enumerate(verified_list) if not x][0] - 1

        if self._marker_counter is None:
            self._marker_counter = -1

        return gdf

    def _main_toolbar(self):
        """
        Generate main toolbar widget
        """
        # Define toolbar padding
        padding = "0px 0px 0px 5px"  # upper, right, bottom, left

        # Define toolbar_button inside Map
        toolbar_button = widgets.ToggleButton(
            value=False,
            tooltip="Toolbar",
            icon="wrench",
            layout=widgets.Layout(
                width="28px", height="28px", padding=padding),
        )

        # Define close_button inside Map
        close_button = widgets.ToggleButton(
            value=False,
            tooltip="Close the tool",
            icon="times",
            button_style="primary",
            layout=widgets.Layout(
                height="28px", width="28px", padding=padding),
        )

        toolbar = widgets.HBox([toolbar_button])

        def close_click(change):
            if change["new"]:
                toolbar_button.close()
                close_button.close()
                toolbar.close()

        close_button.observe(close_click, "value")

        rows = 2
        cols = 2
        grid = widgets.GridspecLayout(
            rows, cols, grid_gap="0px", layout=widgets.Layout(width="62px")
        )

        icons = ["folder-open", "gears", "arrow-left", "arrow-right"]
        for i in range(rows):
            for j in range(cols):
                grid[i, j] = widgets.Button(
                    description="",
                    button_style="primary",
                    icon=icons[i * rows + j],
                    layout=widgets.Layout(width="28px", padding="0px"),
                )

        toolbar = widgets.VBox([toolbar_button])

        def toolbar_click(change):
            if change["new"]:
                toolbar.children = [
                    widgets.HBox([close_button, toolbar_button]), grid]
            else:
                toolbar.children = [toolbar_button]

        toolbar_button.observe(toolbar_click, "value")

        toolbar_ctrl = WidgetControl(widget=toolbar, position="topright")

        self.add_control(toolbar_ctrl)

        output = widgets.Output()
        output_ctrl = WidgetControl(widget=output, position="topright")

        buttons = widgets.ToggleButtons(
            value=None,
            options=["Apply", "Reset", "Close"],
            tooltips=["Apply", "Reset", "Close"],
            button_style="primary",
        )

        # Bands chooser
        red = widgets.Dropdown(
            options=self.default_bands,
            value=self.rgb_bands[0],
            description='Red:',
            disabled=self.rgb_disabled
        )
        green = widgets.Dropdown(
            options=self.default_bands,
            value=self.rgb_bands[1],
            description='Green:',
            disabled=self.rgb_disabled
        )
        blue = widgets.Dropdown(
            options=self.default_bands,
            value=self.rgb_bands[2],
            description='Blue:',
            disabled=self.rgb_disabled
        )

        bands_widget = widgets.HBox([red, green, blue])

        buttons.style.button_width = "80px"

        # Define FileChooser widget
        fc = FileChooser(self.data_dir)
        fc.use_dir_icons = True
        fc.filter_pattern = ["*.tif", "*.gpkg", "*.shp", "*.geojson"]
        filechooser_widget = widgets.VBox([fc, bands_widget, buttons])

        def button_click(change):
            """
            Observer for filechooser_widget button_click
            """
            if change["new"] == "Apply" and fc.selected is not None:

                self._selected_filename = fc.selected

                if self._selected_filename.endswith(".tif"):

                    # Get current bands from widget, add raster to Map
                    data_bands = [item.value for item in bands_widget.children]
                    self.add_raster(
                        self._selected_filename,
                        layer_name="Raster",
                        data_bands=data_bands
                    )

                    # Set output_filename
                    full_dirs = self._selected_filename.split('/')
                    output_dir = os.path.join(
                        self.output_dir,
                        self.username,
                        full_dirs[-3],
                        full_dirs[-2]
                    )
                    os.makedirs(output_dir, exist_ok=True)

                    short_filename = Path(self._selected_filename).stem
                    self.output_filename = os.path.join(
                        output_dir, f"{self.username}-{short_filename}.gpkg")

                    # Visualize or generate markers for validation
                    self.add_markers(
                        self._selected_filename,
                        gen_points=self.gen_points,
                        n_points=self.n_points
                    )

            elif change["new"] == "Reset":
                fc.reset()

            elif change["new"] == "Close":
                fc.reset()
                self.remove_control(output_ctrl)
                buttons.value = None

        buttons.observe(button_click, "value")

        def tool_click(b):
            with output:

                output.clear_output()

                if b.icon == "folder-open":
                    display(filechooser_widget)
                    self.add_control(output_ctrl)

                elif b.icon == "gears":

                    if hasattr(self, "whitebox") \
                            and self.whitebox is not None \
                            and whitebox_imported:
                        if self.whitebox in self.controls:
                            self.remove_control(self.whitebox)

                    tools_dict = wbt.get_wbt_dict()
                    wbt_toolbox = wbt.build_toolbox(
                        tools_dict, max_width="800px", max_height="500px"
                    )

                    wbt_control = WidgetControl(
                        widget=wbt_toolbox, position="bottomright")

                    self.whitebox = wbt_control
                    self.add_control(wbt_control)

                elif b.icon == "arrow-right":
                    self._marker_counter = self._marker_counter + 1
                    if len(list(self._markers_dict)) <= self._marker_counter:
                        self._marker_counter = 0

                    self.center = tuple(
                        list(self._markers_dict)[self._marker_counter])
                    self.zoom = self.default_zoom

                elif b.icon == "arrow-left":
                    self._marker_counter = self._marker_counter - 1
                    if self._marker_counter < 0:
                        self._marker_counter = len(
                            list(self._markers_dict)) - 1

                    self.center = tuple(
                        list(self._markers_dict)[self._marker_counter])
                    self.zoom = self.default_zoom

        for i in range(rows):
            for j in range(cols):
                tool = grid[i, j]
                tool.on_click(tool_click)

        # If the validation database is given, we go straight to
        # load the points into the validation map.
        if self.validation_points_filename is not None \
                and self.marker_type == 'polygon':

            self.add_polygon_markers(self.validation_points_filename)

            # if the validation points from the existing user
            # exist, load those

            # if this is the first time the user is working on this,
            # add the markers directly from this filename

        # TODO: in a future release do the same from a point dataset
        # if self.validation_points_filename is not None \
        # and marker_type == 'point':
